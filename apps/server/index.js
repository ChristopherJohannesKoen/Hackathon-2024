const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const csv = require('csv-parser');

const app = express();
const port = 3001;

app.use(
  cors({
    origin: 'http://localhost:3000',
    methods: 'GET,POST,PUT,DELETE',
  }),
);

app.use(express.json());

const RUNTIME_DIR = path.join(__dirname, 'runTimeData');
const IDS_FILE = path.join(__dirname, 'ids.json');
const SERVICES_FILE = path.join(__dirname, 'services.json');
const RULES_FILE = path.join(__dirname, 'rules.json');

const DEFAULT_WINDOW_MS = 1000 * 60 * 60 * 24 * 4;
const MANUAL_ANOMALY_WINDOW_HOURS = 92;

let services = {};
let ids = {};
let rulesGlobal = {};
let flags = {};

function parseNumber(value, fallback = 0) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function parseTimestamp(value) {
  const timestamp = new Date(value).getTime();
  return Number.isFinite(timestamp) ? timestamp : null;
}

function safeReadJson(filePath, fallbackValue) {
  try {
    if (!fs.existsSync(filePath)) {
      return fallbackValue;
    }

    const rawData = fs.readFileSync(filePath, 'utf8');
    if (!rawData.trim()) {
      return fallbackValue;
    }

    return JSON.parse(rawData);
  } catch (error) {
    console.error(`Failed to read JSON file ${filePath}: ${error.message}`);
    return fallbackValue;
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function runSetupScript() {
  return new Promise((resolve, reject) => {
    exec('python setup.py', (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }

      if (stderr) {
        console.warn(`Python setup stderr: ${stderr}`);
      }

      if (stdout) {
        console.log(`Python setup output: ${stdout}`);
      }

      resolve();
    });
  });
}

function isKnownServiceId(id) {
  return Object.prototype.hasOwnProperty.call(services, id);
}

function getServiceName(id) {
  return services[id];
}

function initializeFlags() {
  flags = {};

  for (const id of Object.keys(services)) {
    // UI expects index 2 to contain the status text.
    flags[id] = [0, 0, 'normal'];
  }
}

function normalizeRulesFileContent(rawRulesContent) {
  const normalizedRules = { global: [] };

  for (const serviceName of Object.values(services)) {
    normalizedRules[serviceName] = [];
  }

  if (!rawRulesContent || typeof rawRulesContent !== 'object') {
    return normalizedRules;
  }

  const candidateRules =
    rawRulesContent.rules && typeof rawRulesContent.rules === 'object'
      ? rawRulesContent.rules
      : rawRulesContent;

  for (const [key, value] of Object.entries(candidateRules)) {
    if (!Array.isArray(value)) {
      continue;
    }

    if (key === 'global') {
      continue;
    }

    if (isKnownServiceId(key)) {
      normalizedRules[services[key]] = value;
      continue;
    }

    normalizedRules[key] = value;
  }

  return normalizedRules;
}

function persistRules() {
  writeJson(RULES_FILE, { rules: rulesGlobal });
}

function loadCsvRows(filePath) {
  return new Promise((resolve, reject) => {
    if (!fs.existsSync(filePath)) {
      resolve([]);
      return;
    }

    const rows = [];

    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => rows.push(row))
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}

function normalizeAndSortRows(rows) {
  return rows
    .map((row) => {
      const timestamp = parseTimestamp(row.usage_end_time);
      return {
        ...row,
        _timestamp: timestamp,
      };
    })
    .filter((row) => row._timestamp !== null)
    .sort((a, b) => a._timestamp - b._timestamp);
}

function aggregateRowsForWindow(rows, windowMs, options = {}) {
  const { combineDuplicates = true, maxPoints = Number.POSITIVE_INFINITY } = options;

  const normalizedRows = normalizeAndSortRows(rows);

  if (normalizedRows.length === 0) {
    return [];
  }

  const lastTimestamp = normalizedRows[normalizedRows.length - 1]._timestamp;
  const firstTimestamp = lastTimestamp - windowMs;

  const windowedRows = normalizedRows.filter((row) => row._timestamp >= firstTimestamp);

  if (!combineDuplicates) {
    const mappedRows = windowedRows.map((row) => ({
      ...row,
      usage_end_time: row._timestamp - firstTimestamp,
    }));

    const clippedRows = Number.isFinite(maxPoints) ? mappedRows.slice(-maxPoints) : mappedRows;
    return clippedRows.map(({ _timestamp, ...rest }) => rest);
  }

  const aggregatedRowsByTime = new Map();

  for (const row of windowedRows) {
    const relativeTimestamp = row._timestamp - firstTimestamp;
    const key = String(relativeTimestamp);

    if (!aggregatedRowsByTime.has(key)) {
      aggregatedRowsByTime.set(key, {
        ...row,
        usage_end_time: relativeTimestamp,
        cost: parseNumber(row.cost),
        usage_amount: parseNumber(row.usage_amount),
      });
      continue;
    }

    const existing = aggregatedRowsByTime.get(key);
    existing.cost += parseNumber(row.cost);
    existing.usage_amount += parseNumber(row.usage_amount);
  }

  const aggregatedRows = [...aggregatedRowsByTime.values()].sort(
    (a, b) => a.usage_end_time - b.usage_end_time,
  );

  const clippedRows = Number.isFinite(maxPoints)
    ? aggregatedRows.slice(-maxPoints)
    : aggregatedRows;

  return clippedRows.map(({ _timestamp, ...rest }) => rest);
}

function buildManualAnomalyResponse(manualAnomalies, windowMs) {
  const normalizedEntries = manualAnomalies
    .map((entry) => ({
      ...entry,
      _timestamp: parseTimestamp(entry.time || entry.usage_end_time),
    }))
    .filter((entry) => entry._timestamp !== null)
    .sort((a, b) => a._timestamp - b._timestamp);

  if (normalizedEntries.length === 0) {
    return [];
  }

  const lastTimestamp = normalizedEntries[normalizedEntries.length - 1]._timestamp;
  const firstTimestamp = lastTimestamp - windowMs;

  return normalizedEntries
    .filter((entry) => entry._timestamp >= firstTimestamp)
    .map((entry) => ({
      usage_end_time: entry._timestamp - firstTimestamp,
      cost: parseNumber(entry.currentValue ?? entry.cost),
      is_anomaly_man: 1,
      anomaly_type_man: entry.detectedRule || entry.anomaly_type_man || 'manual',
    }));
}

async function startupFunction() {
  console.log('Running startup function...');

  try {
    await runSetupScript();
  } catch (error) {
    console.error(`Error executing setup.py: ${error.message}`);
  }

  services = safeReadJson(IDS_FILE, {});
  ids = safeReadJson(SERVICES_FILE, {});

  initializeFlags();

  const rawRulesContent = safeReadJson(RULES_FILE, {});
  rulesGlobal = normalizeRulesFileContent(rawRulesContent);
  persistRules();

  console.log(`Loaded ${Object.keys(services).length} services and ${Object.keys(ids).length} IDs.`);
}

startupFunction();

app.get('/getServices', (_req, res) => {
  res.json(services);
});

app.get('/getFlags', (_req, res) => {
  res.json(flags);
});

app.post('/getDataVariableTime', async (req, res) => {
  const id = String(req.body.id ?? '');
  const requestedWindowMs = Number(req.body.time);
  const windowMs =
    Number.isFinite(requestedWindowMs) && requestedWindowMs > 0
      ? requestedWindowMs
      : DEFAULT_WINDOW_MS;

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const filePath = path.join(RUNTIME_DIR, getServiceName(id), 'data.csv');

  try {
    const rows = await loadCsvRows(filePath);
    const payload = aggregateRowsForWindow(rows, windowMs, { combineDuplicates: true });
    res.json(payload);
  } catch (error) {
    console.error(`Failed to fetch data for ${id}: ${error.message}`);
    res.status(500).json({ error: 'Failed to load data.' });
  }
});

app.post('/getAnonVariableTime', async (req, res) => {
  const id = String(req.body.id ?? '');
  const requestedWindowMs = Number(req.body.time);
  const windowMs =
    Number.isFinite(requestedWindowMs) && requestedWindowMs > 0
      ? requestedWindowMs
      : DEFAULT_WINDOW_MS;

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const filePath = path.join(
    RUNTIME_DIR,
    getServiceName(id),
    'pateStandardDef4V4HourlySumProcessedData.csv',
  );

  try {
    const rows = await loadCsvRows(filePath);
    const payload = aggregateRowsForWindow(rows, windowMs, { combineDuplicates: false });
    res.json(payload);
  } catch (error) {
    console.error(`Failed to fetch anomaly data for ${id}: ${error.message}`);
    res.status(500).json({ error: 'Failed to load anomaly data.' });
  }
});

async function getManualAnomalyVariableTime(req, res) {
  const id = String(req.body.id ?? '');
  const requestedWindowMs = Number(req.body.time);
  const windowMs =
    Number.isFinite(requestedWindowMs) && requestedWindowMs > 0
      ? requestedWindowMs
      : DEFAULT_WINDOW_MS;

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const filePath = path.join(RUNTIME_DIR, getServiceName(id), 'man_anom.json');

  if (!fs.existsSync(filePath)) {
    res.status(200).json([]);
    return;
  }

  try {
    const manualAnomalies = safeReadJson(filePath, []);
    const payload = buildManualAnomalyResponse(
      Array.isArray(manualAnomalies) ? manualAnomalies : [],
      windowMs,
    );

    res.json(payload);
  } catch (error) {
    console.error(`Failed to fetch manual anomalies for ${id}: ${error.message}`);
    res.status(500).json({ error: 'Failed to load manual anomalies.' });
  }
}

// Keep backwards compatibility with the existing typo in the route name.
app.post('/getManaulAnonVariableTime', getManualAnomalyVariableTime);
app.post('/getManualAnonVariableTime', getManualAnomalyVariableTime);

app.post('/getData', async (req, res) => {
  const id = String(req.body.id ?? '');

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const filePath = path.join(RUNTIME_DIR, getServiceName(id), 'data.csv');

  try {
    const rows = await loadCsvRows(filePath);
    const payload = aggregateRowsForWindow(rows, DEFAULT_WINDOW_MS, {
      combineDuplicates: true,
      maxPoints: 100,
    });

    res.json(payload);
  } catch (error) {
    console.error(`Failed to fetch fixed-window data for ${id}: ${error.message}`);
    res.status(500).json({ error: 'Failed to load data.' });
  }
});

app.post('/getServiceName', (req, res) => {
  const id = String(req.body.id ?? '');

  if (!isKnownServiceId(id)) {
    res.status(404).json({ error: 'Unknown service id.' });
    return;
  }

  res.json({ serviceName: getServiceName(id) });
});

app.post('/getRules', (req, res) => {
  const id = String(req.body.id ?? '');

  if (id === 'global') {
    res.json({ rules: rulesGlobal.global || [] });
    return;
  }

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const serviceName = getServiceName(id);
  const serviceRules = rulesGlobal[serviceName] || [];

  res.json({ rules: serviceRules });
});

app.post('/saveRules', async (req, res) => {
  const id = String(req.body.id ?? '');
  const incomingRules = Array.isArray(req.body.rules) ? req.body.rules : [];

  if (id === 'global') {
    rulesGlobal = {
      ...rulesGlobal,
      global: incomingRules,
    };

    try {
      persistRules();
      await updateManualEvents('global');
      res.sendStatus(200);
    } catch (error) {
      console.error(`Error saving global rules: ${error.message}`);
      res.status(500).json({ error: 'Error saving rules.' });
    }
    return;
  }

  if (!isKnownServiceId(id)) {
    res.status(400).json({ error: 'Unknown service id.' });
    return;
  }

  const serviceName = getServiceName(id);

  rulesGlobal = {
    ...rulesGlobal,
    [serviceName]: incomingRules,
  };

  try {
    persistRules();
    await updateManualEvents(id);
    res.sendStatus(200);
  } catch (error) {
    console.error(`Error saving rules for ${serviceName}: ${error.message}`);
    res.status(500).json({ error: 'Error saving rules.' });
  }
});

app.get('/', (_req, res) => {
  res.send('Hello, world!');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

function applyRules(data, serviceRules) {
  if (!Array.isArray(serviceRules) || serviceRules.length === 0) {
    return [];
  }

  const anomalies = [];

  for (const rule of serviceRules) {
    switch (rule.ruleType) {
      case 'Spike Detection':
        applySpikeDetection(data, rule, anomalies);
        break;
      case 'Range':
        applyRangeDetection(data, rule, anomalies);
        break;
      case 'Sudden Change':
        applySuddenChangeDetection(data, rule, anomalies);
        break;
      case 'Gradient':
        applyGradientDetection(data, rule, anomalies);
        break;
      default:
        console.warn(`Unknown rule type: ${rule.ruleType}`);
    }
  }

  return anomalies;
}

function applySpikeDetection(data, rule, anomalies) {
  const threshold = parseNumber(rule.value, Number.NaN);

  if (!Number.isFinite(threshold)) {
    return;
  }

  data.forEach((entry, index) => {
    const windowStart = Math.max(0, index - 24);
    const windowData = data.slice(windowStart, index + 1);

    const avgCost =
      windowData.reduce((sum, item) => sum + parseNumber(item.cost), 0) / windowData.length;

    if (avgCost === 0) {
      return;
    }

    const currentCost = parseNumber(entry.cost);
    const spikePercentage = ((currentCost - avgCost) / avgCost) * 100;

    if (spikePercentage >= threshold) {
      anomalies.push({
        time: entry.usage_end_time,
        service_type: entry.service_type,
        detectedRule: rule.ruleType,
        detectedValue: `${spikePercentage.toFixed(2)}%`,
        averageValue: avgCost,
        currentValue: currentCost,
      });
    }
  });
}

function applyRangeDetection(data, rule, anomalies) {
  const minValue = parseNumber(rule.value1, Number.NaN);
  const maxValue = parseNumber(rule.value2, Number.NaN);

  if (!Number.isFinite(minValue) || !Number.isFinite(maxValue)) {
    return;
  }

  data.forEach((entry) => {
    const cost = parseNumber(entry.cost);

    if (cost < minValue || cost > maxValue) {
      anomalies.push({
        time: entry.usage_end_time,
        service_type: entry.service_type,
        detectedRule: rule.ruleType,
        detectedValue: cost,
        range: `[${minValue}, ${maxValue}]`,
      });
    }
  });
}

function applySuddenChangeDetection(data, rule, anomalies) {
  const threshold = parseNumber(rule.value, Number.NaN);
  const isPercentage = rule.unit === 'percentage';

  if (!Number.isFinite(threshold)) {
    return;
  }

  data.forEach((entry, index) => {
    const baseCost = parseNumber(entry.cost);
    const endIndex = Math.min(data.length - 1, index + 4);

    for (let nextIndex = index + 1; nextIndex <= endIndex; nextIndex += 1) {
      const nextCost = parseNumber(data[nextIndex].cost);

      if (isPercentage && baseCost === 0) {
        continue;
      }

      const diff = isPercentage
        ? Math.abs(((nextCost - baseCost) / baseCost) * 100)
        : Math.abs(nextCost - baseCost);

      if (diff >= threshold) {
        anomalies.push({
          time: entry.usage_end_time,
          service_type: entry.service_type,
          detectedRule: rule.ruleType,
          detectedValue: diff,
          unit: rule.unit,
        });
        break;
      }
    }
  });
}

function applyGradientDetection(data, rule, anomalies) {
  const threshold = parseNumber(rule.value, Number.NaN);
  const direction = rule.unit;

  if (!Number.isFinite(threshold)) {
    return;
  }

  data.forEach((entry, index) => {
    if (index + 9 >= data.length) {
      return;
    }

    const windowData = data.slice(index, index + 10);
    const gradients = [];

    for (let pointIndex = 1; pointIndex < windowData.length; pointIndex += 1) {
      const previous = windowData[pointIndex - 1];
      const current = windowData[pointIndex];

      const timeDelta =
        parseTimestamp(current.usage_end_time) - parseTimestamp(previous.usage_end_time);

      if (!Number.isFinite(timeDelta) || timeDelta === 0) {
        continue;
      }

      const gradient = (parseNumber(current.cost) - parseNumber(previous.cost)) / timeDelta;
      gradients.push(gradient);
    }

    if (gradients.length === 0) {
      return;
    }

    const avgGradient = gradients.reduce((sum, gradient) => sum + gradient, 0) / gradients.length;

    const isAnomaly =
      (direction === 'up' && avgGradient > threshold) ||
      (direction === 'down' && avgGradient < -threshold) ||
      (direction === 'any' && Math.abs(avgGradient) > threshold);

    if (isAnomaly) {
      anomalies.push({
        time: entry.usage_end_time,
        service_type: entry.service_type,
        detectedRule: rule.ruleType,
        detectedValue: avgGradient,
        unit: direction,
      });
    }
  });
}

async function updateManualEvents(targetId) {
  const idsToProcess = targetId === 'global' ? Object.keys(services) : [String(targetId)];

  for (const id of idsToProcess) {
    const serviceName = getServiceName(id);

    if (!serviceName) {
      continue;
    }

    const baseDir = path.join(RUNTIME_DIR, serviceName);
    const csvFilePath = path.join(baseDir, 'data.csv');
    const jsonFilePath = path.join(baseDir, 'man_anom.json');

    if (!fs.existsSync(baseDir)) {
      continue;
    }

    if (!fs.existsSync(jsonFilePath)) {
      writeJson(jsonFilePath, []);
    }

    const serviceRules = Array.isArray(rulesGlobal[serviceName]) ? rulesGlobal[serviceName] : [];
    const globalRules = Array.isArray(rulesGlobal.global) ? rulesGlobal.global : [];
    const rulesForService = [...globalRules, ...serviceRules];

    if (rulesForService.length === 0) {
      writeJson(jsonFilePath, []);
      continue;
    }

    const allRows = await loadCsvRows(csvFilePath);
    const now = Date.now();

    const recentRows = allRows.filter((row) => {
      const timestamp = parseTimestamp(row.usage_end_time);

      if (timestamp === null) {
        return false;
      }

      const elapsedHours = (now - timestamp) / (1000 * 60 * 60);
      return elapsedHours <= MANUAL_ANOMALY_WINDOW_HOURS;
    });

    const anomalies = applyRules(recentRows, rulesForService);
    writeJson(jsonFilePath, anomalies);
  }
}

module.exports = { updateManualEvents };
