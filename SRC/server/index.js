const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3001;

// Cross Origin Resource Sharing, the client is probably running on a different domain
const cors = require('cors');

app.use(cors({
    origin: 'http://localhost:3000',
    methods: 'GET,POST,PUT,DELETE',
}));


app.use(express.json());

const csv = require('csv-parser');



var services = {};
var ids = {};
var rulesGlobal = [];
var flags = [];





// Function that runs on startup
async function startupFunction() {
    console.log('Running startup function...');

    // Execute the Python script
    exec('python setup.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Python script error: ${stderr}`);
            return;
        }

        console.log(`Python script output: ${stdout}`);

        fs.readFile('ids.json', 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading JSON file: ${err.message}`);
                return;
            }
            
            try {
                services = JSON.parse(data);

            } catch (err) {
                console.error(`Error parsing JSON: ${err.message}`);
                return;
            }
      

        fs.readFile('services.json', 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading JSON file: ${err.message}`);
                return;
            }
            
            try {
                ids = JSON.parse(data);
                console.log("IDs Within", ids);

            } catch (err) {
                console.error(`Error parsing JSON: ${err.message}`);
                return;
            }
        


      

            var initialData = {
                global: []
            };
            
            // Create the file again and write the initial data as JSON
            console.log("IDs ", ids);
            for (const id in ids){
                
                initialData[id] =  [];
                flags[services[id]] = [];
                
               

                console.log(services[id]);
                
            }
           // console.log(initialData);
    
            fs.writeFile('rules.json', JSON.stringify(initialData), (err) => {
                if (err) {
                    console.error(`Error writing JSON file: ${err.message}`);
                    return;
                }
            });


            for (const id in services){
                console.log("ID", id);

                //generateAnonomies(id);
            }

        });
    });

    });
      
   
    ;
}


startupFunction(); // Call the startup function


app.get('/getServices', (req, res) => {
    res.send(services);
});

app.get("/getFlags", (req, res) => {
    res.send(flags);
});


app.post('/getDataVariableTime', (req, res) => {    
    const id = req.body.id;
    const time = req.body.time;
    
    console.log(id);
    console.log(time);
        var results = [];
        fs.createReadStream(`./runTimeData/${services[id]}/data.csv`)
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', () => {
        //console.log(results);
    
        const lastResult = results[results.length - 1];
    
        const lastTime = new Date(lastResult.usage_end_time);
    
       // console.log(lastTime);
        const firstTime = new Date(lastTime.getTime() - (time));
      //  console.log(firstTime);
    
        searching = true;
        let i = 0;
        let sendData = [];
        let datapts = 0;
    
        results.reverse();
        sendData[i] = results[i];
        //console.log("END TIME", (new Date(results[i].usage_end_time).getTime()-firstTime));
        sendData[i].usage_end_time = new Date(results[i].usage_end_time).getTime()-firstTime;
        while(searching){
    
            const time = new Date(results[i].usage_end_time).getTime();
            const time2 = new Date(results[i+1].usage_end_time).getTime()-firstTime;
           // console.log(time, "==",time2);
    
            if (time == time2){
                sendData[i].cost = parseFloat(sendData[i].cost) + parseFloat(results[i+1].cost);
                sendData[i].usage_amount = parseFloat(sendData[i].usage_amount) + parseFloat(results[i+1].usage_amount);
    
    
                results.splice(i+1, 1);
    
            }else{
    
                i++;
                sendData[i] = results[i];
                sendData[i].usage_end_time = (new Date(results[i].usage_end_time).getTime())-firstTime;
    
            }
    
            if(i == results.length-1){
                console.log("End of data");
                searching = false;
            }
            else if (sendData[i].usage_end_time<= 0){
                console.log("4 days exceeded")
                searching = false;
            }
           
            
        }
       // console.log(results);
     //  sendData[0].usage_end_time = 0;
        const sendFinal = (sendData.slice(0, i)).reverse();
        console.log(sendFinal);
        res.send(sendFinal);
    
        // You can process your CSV data here
      });
    
    });

    
app.post('/getAnonVariableTime', (req, res) => {    
    const id = req.body.id;
    const time = req.body.time;
    
    console.log(id);
    console.log(time);
        var results = [];
        fs.createReadStream(`./runTimeData/${services[id]}/pateStandardDef4V4HourlySumProcessedData.csv`)
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', () => {
        //console.log(results);
    
        const lastResult = results[results.length - 1];
    
        const lastTime = new Date(lastResult.usage_end_time);
    
       // console.log(lastTime);
        const firstTime = new Date(lastTime.getTime() - (time));
      //  console.log(firstTime);
    
        searching = true;
        let i = 0;
        let sendData = [];
        let datapts = 0;
    
        results.reverse();
        sendData[i] = results[i];
        //console.log("END TIME", (new Date(results[i].usage_end_time).getTime()-firstTime));
        sendData[i].usage_end_time = new Date(results[i].usage_end_time).getTime()-firstTime;
        while(searching){
    
            const time = new Date(results[i].usage_end_time).getTime();
            const time2 = new Date(results[i+1].usage_end_time).getTime()-firstTime;
           // console.log(time, "==",time2);
            
           
                i++;
              
              
                sendData[i] = results[i];
                sendData[i].usage_end_time = (new Date(results[i].usage_end_time).getTime())-firstTime;
                if(results[i].isAnomaly == 1){
                    console.log("Anomaly Detected" , i);
              }
    
            if(i == results.length-1){
                console.log("End of data");
                searching = false;
            }
            else if (sendData[i].usage_end_time<= 0){
                console.log("4 days exceeded")
                searching = false;
            }
           
            
        }
       // console.log(results);
     //  sendData[0].usage_end_time = 0;
        const sendFinal = (sendData.slice(0, i)).reverse();
      //  console.log(sendFinal);
        res.send(sendFinal);
    
        // You can process your CSV data here
      });
    
    });



    app.post('/getManaulAnonVariableTime', (req, res) => {    
        const id = req.body.id;
        const time = req.body.time;
    
        console.log(id);
        console.log(time);
    
        const filePath = path.join(__dirname, `RunTimeData/${services[id]}/man_anom.json`);

        if (!fs.existsSync(filePath)) {
            console.error(`File not found: ${filePath}`);
            res.status(200).send([]);
            return;
        }
    
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                console.error(`Error reading JSON file: ${err.message}`);
                res.status(500).send('Error reading data');
                return;
            }
            
            let manualAnomalies;
            try {
                manualAnomalies = JSON.parse(data);
            } catch (err) {
                console.error(`Error parsing JSON: ${err.message}`);
                res.status(500).send('Error parsing data');
                return;
            }
    
            // Example of processing the JSON data if needed
            // In this example, we assume that no specific time filtering is needed, but you can add filtering if required.
            let firstTime = 0;

const results = manualAnomalies
    .reverse()  // Reverse the order of the array
    .map(entry => {
        if (firstTime === 0) {
            firstTime = new Date(entry.time).getTime() - time;
        }

        return {
            usage_end_time: new Date(entry.time) - firstTime,
            cost: parseFloat(entry.currentValue),  // Assuming 'currentValue' represents the cost
            is_anomaly_man: 1,  // Flag to indicate this is a manual anomaly
            anomaly_type_man: entry.detectedRule,
        };
    });

            
            res.json(results);
        });
    });





app.post('/getData', (req, res) => {
    const id = req.body.id;
    console.log(id);
    var results = [];
    fs.createReadStream(`./runTimeData/${services[id]}/data.csv`)
  .pipe(csv())
  .on('data', (data) => results.push(data))
  .on('end', () => {
    //console.log(results);

    const lastResult = results[results.length - 1];

    const lastTime = new Date(lastResult.usage_end_time);

   // console.log(lastTime);
    const firstTime = new Date(lastTime.getTime() - (1000 * 60 * 60 *24 *4));
  //  console.log(firstTime);

    searching = true;
    let i = 0;
    let sendData = [];
    let datapts = 0;

    results.reverse();
    sendData[i] = results[i];
    //console.log("END TIME", (new Date(results[i].usage_end_time).getTime()-firstTime));
    sendData[i].usage_end_time = new Date(results[i].usage_end_time).getTime()-firstTime;
    while(searching){

        const time = new Date(results[i].usage_end_time).getTime();
        const time2 = new Date(results[i+1].usage_end_time).getTime()-firstTime;
       // console.log(time, "==",time2);

        if (time == time2){
            sendData[i].cost = parseFloat(sendData[i].cost) + parseFloat(results[i+1].cost);
            sendData[i].usage_amount = parseFloat(sendData[i].usage_amount) + parseFloat(results[i+1].usage_amount);


            results.splice(i+1, 1);

        }else{

            i++;
            sendData[i] = results[i];
            sendData[i].usage_end_time = (new Date(results[i].usage_end_time).getTime())-firstTime;

        }

        if(i == results.length-1){
            console.log("End of data");
            searching = false;
        }
        else if (sendData[i].usage_end_time<= 0){
            console.log("4 days exceeded")
            searching = false;
        }else if (i >= 100){
            searching = false;
            console.log("10000 datapoints reached");

        }
       
        
    }
   // console.log(results);
 //  sendData[0].usage_end_time = 0;
    const sendFinal = (sendData.slice(0, i)).reverse();
    console.log(sendFinal);
    res.send(sendFinal);

    // You can process your CSV data here
  });

});

app.post('/getServiceName', (req, res) => {
    const id = req.body.id;
    console.log(id);

    console.log(services[id]);
    res.send(JSON.stringify({'serviceName': services[id]}));
});

app.post('/getRules', (req, res) => {
    const id = req.body.id;

    console.log('ID:', id);

    try {
        // Read the rules from the file
        const filePath = path.join(__dirname, 'rules.json');
        const rulesFile = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        // Retrieve the rules for the specific id
        const rules = rulesFile['rules'][services[id]];

        console.log('Retrieved Rules:', rules);

        // Send the rules back to the client
        res.send(JSON.stringify({ 'rules': rules }));

    } catch (err) {
        console.error(`Error reading JSON file: ${err.message}`);
        res.status(500).send('Error retrieving rules.');
    }
}); 


app.post('/saveRules', (req, res) => {    
    const id = req.body.id;
    const rules = req.body.rules;

    console.log('ID:', id);
    console.log('Rules:', rules);

    // Create a deep copy of rulesGlobal to ensure it is updated correctly
    const updatedRulesGlobal = { ...rulesGlobal };

    // Update the rulesGlobal object
    updatedRulesGlobal[services[id]] = rules;

    console.log('Service:', services[id]);
    console.log('Updated rulesGlobal:', updatedRulesGlobal);
    rulesGlobal = updatedRulesGlobal;

    // Define the path to the file
    const filePath = path.join(__dirname, 'rules.json');

    try {
        // Check if the file exists, if so, delete it
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            console.log('Existing file deleted.');
        }

        // Write the updated rulesGlobal object to the file
        fs.writeFileSync(filePath, JSON.stringify({ 'rules': updatedRulesGlobal }, null, 2));
        console.log('Rules saved to file:', updatedRulesGlobal);
        updateManualEvents(id);
        res.sendStatus(200);
    } catch (err) {
        console.error(`Error handling JSON file: ${err.message}`);
        res.status(500).send('Error saving rules.');
    }

   
});




app.get('/', (req, res) => {
    res.send('Hello, world!');
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});



function generateAnonomies(id) {
    
    console.log("Runnung script ", id, "targeted at ", services[id]);
    exec('python PateIsoTree4V1PointExtractLast96Hours.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Python script error: ${stderr}`);
            return;
        }
        if (stdout) {
            console.log(`Python script output: ${stdout}`);
        }

    });


}

function updateManualEvents(id) {
    // Assuming services[id] returns the service name as a string
    const serviceName = services[id];
    if (!serviceName) {
        console.error(`Service name for ID ${id} is not defined`);
        return;
    }

    const baseDir = path.join(__dirname, 'runTimeData', serviceName);
    console.log(`Base Directory: ${baseDir}`);

    function processId(id) {
        const csvFilePath = path.join(baseDir, 'data.csv');
        const jsonFilePath = path.join(baseDir, 'man_anom.json');

        if (!fs.existsSync(jsonFilePath)) {
            fs.writeFileSync(jsonFilePath, JSON.stringify([], null, 2));
            console.log(`Created ${jsonFilePath}`);
        }

        const rules = rulesGlobal//[serviceName]; // Use the correct service name to access rules

        // Handle the case where no rules are defined for the service
        if (!rules) {
            console.log(`No rules defined for service ${serviceName}. Skipping...`);
            return;
        }

        // Debugging output
        console.log(`Processing ${id} (Service: ${serviceName})...`);
        console.log(`Rules for service ${serviceName}:`, JSON.stringify(rules, null, 2));

        console.log(`Rules,` , rules);

        

       

        const last92HoursData = [];

        fs.createReadStream(csvFilePath)
            .pipe(csv())
            .on('data', (row) => {
                const usageEndTime = new Date(row.usage_end_time);
                const now = new Date();
                const diffHours = (now - usageEndTime) / (1000 * 60 * 60);

                if (diffHours <= 92) {
                    last92HoursData.push(row);
                }
               // console.log("Last 92 Hours Data", last92HoursData);
            })
            .on('end', () => {
                console.log("Applying Rules");
                console.log('Rules:', JSON.stringify(rules, null, 2)); // Logging the rules again before applying
                const anomalies = applyRules(last92HoursData, rules);
                fs.writeFileSync(jsonFilePath, JSON.stringify(anomalies, null, 2));
                console.log(`Anomalies for ${id} saved to ${jsonFilePath}`);
            });
    }

    if (id === 'global') {
        global.ids.forEach((id) => {
            processId(id);
        });
    } else {
        processId(id);
    }
}

// Apply rules function (applyRules) and related sub-functions (applySpikeDetection, applyRangeDetection, etc.) would go here, unchanged from the previous example.

module.exports = { updateManualEvents };



    function applyRules(data, rules) {
        const anomalies = [];
    
        console.log('Rules:', JSON.stringify(rules, null, 2));
    
        Object.keys(rules).forEach((serviceName) => {
            const serviceRules = rules[serviceName];
    
            if (Array.isArray(serviceRules)) {
                console.log('Service Rules for', serviceName, ':', JSON.stringify(serviceRules, null, 2));
    
                serviceRules.forEach((rule) => {
                    const threshold = parseFloat(rule.value);
    
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
                });
            } else {
                console.warn(`Rules for service ${serviceName} are not in the expected array format.`);
            }
        });
    
        return anomalies;
    }
    

    function applySpikeDetection(data, rule, anomalies) {
        const threshold = parseFloat(rule.value);

        data.forEach((entry, index) => {
            const windowStart = Math.max(0, index - 24);
            const windowData = data.slice(windowStart, index + 1);

            const avgCost = windowData.reduce((sum, d) => sum + parseFloat(d.cost), 0) / windowData.length;

            const spikePercentage = ((entry.cost - avgCost) / avgCost) * 100;

            if (spikePercentage >= threshold) {
                anomalies.push({
                    time: entry.usage_end_time,
                    service_type: entry.service_type,
                    detectedRule: rule.ruleType,
                    detectedValue: spikePercentage.toFixed(2) + '%',
                    averageValue: avgCost,
                    currentValue: entry.cost
                });
            }
        });
    }

    function applyRangeDetection(data, rule, anomalies) {
        const minValue = parseFloat(rule.value1);
        const maxValue = parseFloat(rule.value2);

        data.forEach((entry) => {
            const cost = parseFloat(entry.cost);
            if (cost < minValue || cost > maxValue) {
                anomalies.push({
                    time: entry.usage_end_time,
                    service_type: entry.service_type,
                    detectedRule: rule.ruleType,
                    detectedValue: cost,
                    range: `[${minValue}, ${maxValue}]`
                });
            }
        });
    }

    function applySuddenChangeDetection(data, rule, anomalies) {
        const threshold = parseFloat(rule.value);
        const isPercentage = rule.unit === 'percentage';

        data.forEach((entry, index) => {
            const endIndex = Math.min(data.length - 1, index + 4);
            for (let i = index + 1; i <= endIndex; i++) {
                const diff = isPercentage
                    ? Math.abs(((data[i].cost - entry.cost) / entry.cost) * 100)
                    : Math.abs(data[i].cost - entry.cost);

                if (diff >= threshold) {
                    anomalies.push({
                        time: entry.usage_end_time,
                        service_type: entry.service_type,
                        detectedRule: rule.ruleType,
                        detectedValue: diff,
                        unit: rule.unit
                    });
                    break;
                }
            }
        });
    }

    function applyGradientDetection(data, rule, anomalies) {
        const threshold = parseFloat(rule.value);
        const direction = rule.unit;

        data.forEach((entry, index) => {
            if (index + 9 < data.length) {
                const windowData = data.slice(index, index + 10);
                const gradients = [];

                for (let i = 1; i < windowData.length; i++) {
                    const gradient = (windowData[i].cost - windowData[i - 1].cost) / (new Date(windowData[i].usage_end_time) - new Date(windowData[i - 1].usage_end_time));
                    gradients.push(gradient);
                }

                const avgGradient = gradients.reduce((sum, g) => sum + g, 0) / gradients.length;

                let isAnomaly = false;
                if (direction === 'up' && avgGradient > threshold) {
                    isAnomaly = true;
                } else if (direction === 'down' && avgGradient < -threshold) {
                    isAnomaly = true;
                } else if (direction === 'any' && Math.abs(avgGradient) > threshold) {
                    isAnomaly = true;
                }

                if (isAnomaly) {
                    anomalies.push({
                        time: entry.usage_end_time,
                        service_type: entry.service_type,
                        detectedRule: rule.ruleType,
                        detectedValue: avgGradient,
                        unit: direction
                    });
                }
            }
        });
    }



