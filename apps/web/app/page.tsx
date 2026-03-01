'use client'

import Link from "next/link"
import { LinechartChart } from "@/components/component/LinechartChart"

import { useState, useEffect } from "react"
//import Router from "next/router"

import { useRouter } from "next/navigation"

type ServiceMap = Record<string, string>;
type ServiceFlag = [number, number, string];
type FlagMap = Record<string, ServiceFlag>;
type GraphDataMap = Record<string, any[]>;

export default function Dashboard() {
  const [services, setServices] = useState<ServiceMap>({});
  const [flags, setFlags] = useState<FlagMap>({});
  const [graphData, setGraphData] = useState<GraphDataMap>({});
  const [loading, setLoading] = useState(true);
  
  const router = useRouter()
 

  const handleClick = (key: string) =>{
    console.log(key);
    router.push(`/focus/${key}`)
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const servicesResponse = await fetch('http://localhost:3001/getServices', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        const servicesData = await servicesResponse.json();
        setServices(servicesData);

        const flagsResponse = await fetch('http://localhost:3001/getFlags', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        const flagsData = await flagsResponse.json();
        setFlags(flagsData);
        setLoading(false);
        console.log("Loading Complete")
        for (const key in servicesData) {
          const JSONBody = JSON.stringify({ id: key });
          const graphResponse = await fetch('http://localhost:3001/getData', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSONBody
          });
          const graphDataItem = await graphResponse.json();
          
          // Update the graph data incrementally
          setGraphData((prevGraphData) => ({
            ...prevGraphData,
            [key]: graphDataItem
          }));
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Loading data...</p>
      </div>
    );
  }

  if (!Object.keys(services).length) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>No services available.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full min-h-screen bg-muted/40">
      <header className="flex items-center h-16 px-4 border-b shrink-0 md:px-6">
        <Link href="#" className="flex items-center gap-2 text-lg font-semibold sm:text-base mr-4" prefetch={false}>
          <FrameIcon className="w-6 h-6" />
          <span className="sr-only">Anomaly Detection Dashboard</span>
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
            <h1 className="text-2xl font-bold tracking-tight">Anomaly Detection Dashboard</h1>
            <p className="text-muted-foreground">Monitor the health of your cloud services in real-time.</p>
          </div>
        
        </div>
        <div className="grid gap-4 md:grid-cols-4 md:w-[80%] mx-auto">
          {Object.keys(services).map((key) => (
           <div
           key={key}
           onClick={() => handleClick(key)}
           className={`flex flex-col items-center justify-center p-4 rounded-lg aspect-square transition-colors ${
             flags[key] && flags[key][2] === "alert"
               ? "bg-red-500/30 hover:bg-red-500/20"
               : flags[key] && flags[key][2] === "warning"
               ? "bg-yellow-500/30 hover:bg-yellow-500/20"
               : "bg-green-500/30 hover:bg-green-500/20"
           }`}
         >
              <div className="text-2xl font-bold">
                {services[key]}
              </div>

              <div
                className={`text-sm font-medium ${flags[key] && (flags[key][2] === "alert")
                  ? "text-red-500"
                  : flags[key] && (flags[key][2] === "warning")
                    ? "text-yellow-500"
                    : "text-green-500"
                  }`}
              >
                {flags[key] ? flags[key][2].toUpperCase(): "NORMAL"}
              </div>
              
              {graphData[key] ? (
                <LinechartChart data={graphData[key]} />
              ) : (
                <div>Loading graph...</div>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}

function FrameIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="22" x2="2" y1="6" y2="6" />
      <line x1="22" x2="2" y1="18" y2="18" />
      <line x1="6" x2="6" y1="2" y2="22" />
      <line x1="18" x2="18" y1="2" y2="22" />
    </svg>
  )
}
