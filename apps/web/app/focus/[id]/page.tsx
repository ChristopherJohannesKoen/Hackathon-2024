"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import Settings from "@/components/component/settings";
import SnapSlider from "@/components/component/slider";
import { useParams } from "next/navigation";

const ONE_DAY_MS = 1000 * 60 * 60 * 24;

function sliderToWindowMs(value: number) {
  switch (value) {
    case 1:
      return ONE_DAY_MS;
    case 2:
      return ONE_DAY_MS * 4;
    case 3:
      return ONE_DAY_MS * 7;
    case 4:
      return ONE_DAY_MS * 30;
    case 5:
      return ONE_DAY_MS * 365;
    default:
      return ONE_DAY_MS * 365 * 10;
  }
}

export default function FocusPage() {
  const { id } = useParams();
  const serviceId = Array.isArray(id) ? id[0] : id;

  const [serviceName, setServiceName] = useState("loading..");
  const [combinedData, setCombinedData] = useState<any[]>([]);
  const [sliderValue, setSliderValue] = useState(1);
  const [serviceState, setServiceState] = useState("normal");

  const fetchDataAndCombine = useCallback(async (windowMs: number) => {
    if (!serviceId) {
      return;
    }

    try {
      const requestBody = JSON.stringify({ id: serviceId, time: windowMs });

      const [dataResponse, anomalyResponse, manualAnomalyResponse] = await Promise.all([
        fetch("http://localhost:3001/getDataVariableTime", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: requestBody,
        }),
        fetch("http://localhost:3001/getAnonVariableTime", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: requestBody,
        }),
        fetch("http://localhost:3001/getManaulAnonVariableTime", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: requestBody,
        }),
      ]);

      const [graphData, anomalyData, manualAnomalyData] = await Promise.all([
        dataResponse.json(),
        anomalyResponse.json(),
        manualAnomalyResponse.json(),
      ]);

      const transformedAutoAnomalies = anomalyData
        .map((entry: any) => ({
          usage_end_time: entry.usage_end_time ?? null,
          cost: entry.cost ?? 0,
          is_anomaly: Number(entry.is_anomaly ?? entry.isAnomaly ?? 0),
          anomaly_type: entry.anomaly_type ?? "unknown",
        }))
        .filter((entry: any) => entry.is_anomaly === 1);

      const transformedManualAnomalies = manualAnomalyData
        .map((entry: any) => ({
          usage_end_time: entry.usage_end_time ?? null,
          cost: entry.cost ?? 0,
          is_anomaly_man: Number(entry.is_anomaly_man ?? 0),
          anomaly_type_man: entry.anomaly_type_man ?? "manual",
        }))
        .filter((entry: any) => entry.is_anomaly_man === 1);

      setServiceState(
        transformedAutoAnomalies.length > 0 || transformedManualAnomalies.length > 0
          ? "alert"
          : "normal",
      );

      const mergedData = graphData.map((dataPoint: any) => {
        const autoAnomaly = transformedAutoAnomalies.find(
          (anomaly: any) => anomaly.usage_end_time === dataPoint.usage_end_time,
        );
        const manualAnomaly = transformedManualAnomalies.find(
          (anomaly: any) => anomaly.usage_end_time === dataPoint.usage_end_time,
        );

        return {
          ...dataPoint,
          anomaly_value: autoAnomaly ? autoAnomaly.cost : null,
          is_anomaly: autoAnomaly ? autoAnomaly.is_anomaly : 0,
          anomaly_type: autoAnomaly ? autoAnomaly.anomaly_type : null,
          anomaly_value_man: manualAnomaly ? manualAnomaly.cost : null,
          is_anomaly_man: manualAnomaly ? manualAnomaly.is_anomaly_man : 0,
          anomaly_type_man: manualAnomaly ? manualAnomaly.anomaly_type_man : null,
        };
      });

      setCombinedData(mergedData);
    } catch (error) {
      console.error("Error fetching focus data:", error);
    }
  }, [serviceId]);

  useEffect(() => {
    if (!serviceId) {
      return;
    }

    const fetchServiceName = async () => {
      try {
        const response = await fetch("http://localhost:3001/getServiceName", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: serviceId }),
        });
        const data = await response.json();
        setServiceName(data.serviceName ?? "Unknown service");
      } catch (error) {
        console.error("Error fetching service name:", error);
        setServiceName("Unknown service");
      }
    };

    fetchServiceName();
    fetchDataAndCombine(ONE_DAY_MS);
  }, [serviceId, fetchDataAndCombine]);

  const handleSlider = (value: number) => {
    setSliderValue(value);
    fetchDataAndCombine(sliderToWindowMs(value));
  };

  return (
    <div className="flex flex-col w-full min-h-screen bg-muted/40">
      <header className="flex items-center h-16 px-4 border-b shrink-0 md:px-6">
        <Link
          href="#"
          className="flex items-center gap-2 text-lg font-semibold sm:text-base mr-4"
          prefetch={false}
        >
          <div className="w-6 h-6" />
          <span className="sr-only">Focused View</span>
        </Link>
        <nav className="hidden font-medium sm:flex flex-row items-center gap-5 text-sm lg:gap-6">
          <Link href="/" className="font-bold" prefetch={false}>
            Dashboard
          </Link>
          <Link href="/reports" className="text-muted-foreground" prefetch={false}>
            Reports
          </Link>
          <Link href="/globalsettings" className="text-muted-foreground" prefetch={false}>
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
                className={`font-medium ${
                  serviceState === "normal"
                    ? "text-green-500"
                    : serviceState === "warning"
                      ? "text-yellow-500"
                      : "text-red-500"
                }`}
              >
                {serviceState.toUpperCase()}
              </div>
            </div>
          </div>
          <SnapSlider values={[sliderValue]} onChange={handleSlider} />
        </div>

        <div className="bg-background rounded-lg p-6 shadow">
          <div className="w-full h-80 aspect-[4/3]">
            <h1>Detailed Graph</h1>

            <ResponsiveContainer>
              <LineChart
                data={combinedData}
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
                  tick={false}
                />
                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="cost"
                  stroke="#8884d8"
                  fill="#8884d8"
                  opacity={0.5}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="anomaly_value"
                  stroke="#8884d8"
                  fill="#FF0000"
                  opacity={0.5}
                  dot={{ r: 8 }}
                />
                <Line
                  type="monotone"
                  dataKey="anomaly_value_man"
                  stroke="#8884d8"
                  fill="#FF00FF"
                  opacity={0.5}
                  dot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <Settings service={serviceName} id={serviceId ?? ""} />
      </main>
    </div>
  );
}
