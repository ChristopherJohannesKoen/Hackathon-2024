"use client"

import React, { useState, useEffect } from "react"
import Link from "next/link"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Scatter } from 'recharts';
import { Button } from "@/components/ui/button"
import Settings from "@/components/component/settings"
import SnapSlider from "@/components/component/slider"
import { useParams } from "next/navigation"

export default function Component() {
  const [showSettings, setShowSettings] = useState(false)
  const [serviceName, setServiceName] = useState("loading..")
  const [graphData, setGraphData] = useState([]);
  const [filteredAnonData, setFilteredAnonData] = useState([]);
  const [filteredAnonManData, setFilteredAnonManData] = useState([]);
  const [combinedData, setCombinedData] = useState([]);
  const { id } = useParams()
  const [sliderValue, setSliderValue] = useState(1);
  const [serviceState, setServiceState] = useState("normal");
  const [firstLoad, setFirstLoad] = useState(true);

  const handleSlider = (value) => {
    setSliderValue(value)
    console.log(value)
    let seconds = 0;
    switch (value) {
      case 1:
        seconds = 1000 * 60 * 60 * 24
        break;
      case 2:
        seconds = 1000 * 60 * 60 * 24 * 4
        break;
      case 3:
        seconds = 1000 * 60 * 60 * 24 * 7
        break;
      case 4:
        seconds = 1000 * 60 * 60 * 24 * 30
        break;
      case 5:
        seconds = 1000 * 60 * 60 * 24 * 365
        break;
      default:
        seconds = 1000 * 60 * 60 * 24 * 365 * 10
        break;
    }

    fetchDataAndCombine(seconds);
  }

  const fetchDataAndCombine = (seconds) => {
    fetch(`http://localhost:3001/getDataVariableTime`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 'id': id, 'time': seconds })
    }).then(response => response.json())
      .then(data => {
        console.log(data)
        setGraphData(data);

        fetch(`http://localhost:3001/getAnonVariableTime`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 'id': id, 'time': seconds })
        }).then(response => response.json())
          .then(anonData => {
            console.log("Anomaly Data:", anonData);
            const transformedData = anonData.map(entry => ({
              usage_end_time: entry.usage_end_time || null,
              cost: entry.cost || 0,
              is_anomaly: entry.is_anomaly || 0,
              anomaly_type: entry.anomaly_type || 'unknown',
              anomaly_value: entry.is_anomaly ? entry.cost : 0,
            }));
            const filteredData = transformedData.filter(entry => entry.is_anomaly == 1);

            console.log("Filtered Anomaly Data:", filteredData);
            if (filteredData.length > 0) {
              setServiceState("alert")
            }
            setFilteredAnonData(filteredData); // Store the filtered data

            // Fetch manual anomaly data
            fetch(`http://localhost:3001/getManaulAnonVariableTime`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'id': id, 'time': seconds })
            }).then(response => response.json())
              .then(anonManData => {
                console.log("Manual Anomaly Data:", anonManData);
                const transformedManData = anonManData.map(entry => ({
                  usage_end_time: entry.usage_end_time || null,
                  cost: entry.cost || 0,
                  is_anomaly_man: entry.is_anomaly_man || 0,
                  anomaly_type_man: entry.anomaly_type_man || 'manual',
                  anomaly_value_man: entry.is_anomaly_man ? entry.cost : 0,
                }));
                const filteredManData = transformedManData.filter(entry => entry.is_anomaly_man == 1);

                console.log("Filtered Manual Anomaly Data:", filteredManData);
                setFilteredAnonManData(filteredManData); // Store the manual anomaly data

                // Combine graphData, filteredAnonData, and filteredAnonManData
                const combined = data.map(dataPoint => {
                  const anomaly = filteredData.find(anon => anon.usage_end_time === dataPoint.usage_end_time);
                  const anomalyMan = filteredManData.find(anonMan => anonMan.usage_end_time === dataPoint.usage_end_time);
                  return {
                    ...dataPoint,
                    anomaly_value: anomaly ? anomaly.cost : null,
                    is_anomaly: anomaly ? anomaly.is_anomaly : 0,
                    anomaly_type: anomaly ? anomaly.anomaly_type : null,
                    anomaly_value_man: anomalyMan ? anomalyMan.cost : null,
                    is_anomaly_man: anomalyMan ? anomalyMan.is_anomaly_man : 0,
                    anomaly_type_man: anomalyMan ? anomalyMan.anomaly_type_man : null,
                  };
                });
                setCombinedData(combined);
                console.log("Combined Data:", combined);
              });
          });
      });
  }

  useEffect(() => {
    console.log("fetching service name")
    fetch(`http://localhost:3001/getServiceName`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 'id': id })
    }).then(response => response.json())
      .then(data => {
        setServiceName(data.serviceName)
      })

    if (firstLoad) {
      fetchDataAndCombine(3600 * 24);  // Fetch initial data for one day
      setFirstLoad(false);
    }
  }, [firstLoad]);

  return (
    <div className="flex flex-col w-full min-h-screen bg-muted/40">
      <header className="flex items-center h-16 px-4 border-b shrink-0 md:px-6">
        <Link href="#" className="flex items-center gap-2 text-lg font-semibold sm:text-base mr-4" prefetch={false}>
          <div className="w-6 h-6" />
          <span className="sr-only">Focused View</span>
        </Link>
        <nav className="hidden font-medium sm:flex flex-row items-center gap-5 text-sm lg:gap-6">
          <Link href="/" className="font-bold" prefetch={false}>
            Dashboard
          </Link>
          <Link href="/repor" className="text-muted-foreground" prefetch={false}>
            Reports
          </Link>
          <Link href="/globalRules" className="text-muted-foreground" prefetch={false}>
            Settings
          </Link>
        </nav>
      </header>

      <main className="flex-1 flex flex-col gap-4 p-4 md:gap-8 md:p-10">
        <div className="flex items-center justify-between">
          <div className="grid gap-1">
            <h1 className="text-2xl font-bold tracking-tight">{serviceName}</h1>
            <div className="flex items-center gap-2">
              <div
                className={`font-medium  ${serviceState === "normal"
                  ? "text-green-500"
                  : serviceState === "warning"
                    ? "text-yellow-500"
                    : "text-red-500"
                  }`}
              >{serviceState.toUpperCase()}</div>
            </div>
          </div>
          <SnapSlider values={[sliderValue]} onChange={handleSlider}></SnapSlider>
        </div>

        <div className="bg-background rounded-lg p-6 shadow">
          <div className="w-full h-80 aspect-[4/3]" >
            <h1>Detailed Graph</h1>

            <ResponsiveContainer>
              <LineChart
                data={combinedData} // Use the combined data
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="usage_end_time"
                  label={{ value: "Time", position: "insideBottomRight", offset: -5 }}
                />
                <YAxis
                  label={{ value: "Cost", angle: -90, position: "insideLeft" }}
                  tick={false} // Hide the Y-axis ticks
                />
                <Tooltip />

                {/* Main Line for combined data */}
                 <Line
                  type="monotone"
                  dataKey="cost"
                  stroke="#8884d8"
                  fill="#8884d8"
                  opacity={0.5}
                  dot={false}  // Disable icons at data points for graphData
                />

                {/* Scatter plot for anomalies */}
                <Line
                  type="monotone"
                  dataKey="anomaly_value"
                  stroke="#8884d8"
                  fill="#FF0000"
                  opacity={0.5}
                  dot={{r: 8}}  // Disable icons at data points for graphData
                /> 

                {/* Scatter plot for manual anomalies */}
                <Line
                  type="monotone"
                  dataKey="anomaly_value_man"
                  stroke="#8884d8"
                  fill="#FF00FF"
                  opacity={0.5}
                  dot={{r: 8}}  // Disable icons at data points for graphData
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <Settings service={serviceName} id={id}></Settings>
      </main>
    </div>
  )
}

// Additional icons functions remain unchanged...
