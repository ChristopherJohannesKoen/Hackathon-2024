import React, { useState, useEffect } from 'react';

interface Rule {
  ruleType: string;
  value?: string;
  value1?: string;
  value2?: string;
  unit?: string;
}

interface ManualAlertingProps {
  service?: string;
  id?: string;
}

const ManualAlerting = ({ service, id }: ManualAlertingProps) => {
  const [ruleType, setRuleType] = useState('Spike Detection');
  const [value1, setValue1] = useState('');
  const [value2, setValue2] = useState('');
  const [unit, setUnit] = useState('% away from daily average');
  const [rules, setRules] = useState<Rule[]>([]);
  const [manualRulesEnabled, setManualRulesEnabled] = useState(false);

  useEffect(() => {
    // Fetch existing rules when the component loads
    const fetchRules = async () => {
      try {
        const response = await fetch('http://localhost:3001/getRules', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ id }),
        });
        const data = await response.json();
        const loadedRules = Array.isArray(data.rules) ? data.rules : [];
        setRules(loadedRules);
        setManualRulesEnabled(loadedRules.length > 0);
      } catch (error) {
        console.error('Failed to fetch rules:', error);
      }
    };

    fetchRules();
  }, [id]);

  const handleAddRule = async () => {
    const newRule = ruleType === 'Range' 
      ? { ruleType, value1, value2 } 
      : { ruleType, value: value1, unit };

    const updatedRules = [...rules, newRule];
    setRules(updatedRules);
    setManualRulesEnabled(true);
    await saveRules(updatedRules);

    resetForm();
  };

  const handleDeleteRule = async (index: number) => {
    const updatedRules = rules.filter((_, i) => i !== index);
    setRules(updatedRules);
    await saveRules(updatedRules);
  };

  const handleEditRule = async (index: number) => {
    const ruleToEdit = rules[index];
    if (!ruleToEdit) {
      return;
    }

    setRuleType(ruleToEdit.ruleType);

    if (ruleToEdit.ruleType === 'Range') {
      setValue1(ruleToEdit.value1 ?? '');
      setValue2(ruleToEdit.value2 ?? '');
      setUnit('');
    } else {
      setValue1(ruleToEdit.value ?? '');
      setValue2('');
      setUnit(ruleToEdit.unit ?? '% away from daily average');
    }

    const updatedRules = rules.filter((_, i) => i !== index);
    setRules(updatedRules);
    await saveRules(updatedRules);
  };

  const saveRules = async (updatedRules: Rule[]) => {
    try {
      const response = await fetch('http://localhost:3001/saveRules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, rules: updatedRules }),
      });

      if (!response.ok) {
        throw new Error('Failed to save rules');
      }
    } catch (error) {
      console.error('Failed to save rules:', error);
    }
  };

  const resetForm = () => {
    setRuleType('Spike Detection');
    setValue1('');
    setValue2('');
    setUnit('% away from daily average');
  };

  const handleRuleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedRuleType = e.target.value;
    setRuleType(selectedRuleType);
    setValue1('');
    setValue2('');
    switch (selectedRuleType) {
      case 'Spike Detection':
        setUnit('% away from daily average');
        break;
      case 'Sudden Change':
        setUnit('percentage');
        break;
      case 'Gradient':
        setUnit('up');
        break;
      default:
        setUnit('');
        break;
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white shadow-lg rounded-lg">
      <h1 className="text-2xl font-bold mb-4">Manual Alerting</h1>
      <h2 className="text-xl font-semibold mb-2">{service}</h2>
      <p className="mb-6">Configure monitoring and alerting rules for your application.</p>

      {!manualRulesEnabled ? (
        <div className="flex items-center justify-center">
          <button
            onClick={() => setManualRulesEnabled(true)}
            className="py-2 px-4 bg-blue-600 text-white font-semibold rounded-md shadow hover:bg-blue-500"
          >
            Enable Manual Rules
          </button>
        </div>
      ) : (
        <div>
          <div className="mb-4">
            <label htmlFor="ruleType" className="block text-left font-medium mb-2">Rule Type</label>
            <select
              id="ruleType"
              className="w-full p-2 border border-gray-300 rounded-md"
              value={ruleType}
              onChange={handleRuleTypeChange}
            >
              <option value="Range">Range</option>
              <option value="Spike Detection">Spike Detection</option>
              <option value="Gradient">Gradient</option>
              <option value="Sudden Change">Sudden Change</option>
            </select>
          </div>

          <label className="block text-left font-medium mb-2">Trigger alert when:</label>
          {ruleType === 'Range' ? (
            
            <div className="flex space-x-2 mb-4">
              <span className='self-center'>Out of range: </span>
              <input
                type="text"
                className="w-1/3 p-2 border border-gray-300 rounded-md"
                value={value1}
                onChange={(e) => setValue1(e.target.value)}
                placeholder="Value 1"
              />
              <span className="self-center">to</span>
              <input
                type="text"
                className="w-1/3 p-2 border border-gray-300 rounded-md"
                value={value2}
                onChange={(e) => setValue2(e.target.value)}
                placeholder="Value 2"
              />
            </div>
          ) : (
            <div className="flex space-x-2 mb-4">
              <input
                type="text"
                className="flex-1 p-2 border border-gray-300 rounded-md"
                value={value1}
                onChange={(e) => setValue1(e.target.value)}
                placeholder="Value"
              />
              <select
                id="unit"
                className="w-1/2 p-2 border border-gray-300 rounded-md"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
              >
                {ruleType === 'Spike Detection' && (
                  <option value="% away from daily average">% away from daily average</option>
                )}
                {ruleType === 'Sudden Change' && (
                  <>
                    <option value="percentage">Percentage</option>
                    <option value="value">Value</option>
                  </>
                )}
                {ruleType === 'Gradient' && (
                  <>
                    <option value="up">Up</option>
                    <option value="down">Down</option>
                    <option value="any">Any</option>
                  </>
                )}
              </select>
            </div>
          )}

          <button
            onClick={handleAddRule}
            className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md shadow hover:bg-blue-500 disabled:bg-gray-400"
            disabled={!value1 || (ruleType === 'Range' && !value2)}
          >
            Add Rule
          </button>

          <div className="mt-6">
            {rules.length > 0 && (
              <ul className="space-y-4">
                {rules.map((rule, index) => (
                  <li key={index} className="w-full p-4 bg-gray-100 rounded-md shadow-md">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold">{rule.ruleType}</p>
                        {rule.ruleType === 'Range' ? (
                          <p>
                            Outside of range {rule.value1} to {rule.value2}
                          </p>
                        ) : (
                          <p>
                            {rule.value} {rule.unit}
                          </p>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEditRule(index)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteRule(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ManualAlerting;
