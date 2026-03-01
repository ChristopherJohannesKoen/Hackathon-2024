"use client";

import * as React from "react";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

type ReportLevel = "warning" | "alert";

interface ReportItem {
  name: string;
  time: string;
  level: ReportLevel;
  cause: string;
}

const data: Record<string, ReportItem[]> = {
  "0": [
    { name: "google", time: "1723910057", level: "alert", cause: "53.96% Spike in usage" },
    { name: "google", time: "1723910032", level: "warning", cause: "Out of specified range" },
  ],
  "1": [
    { name: "aws", time: "1723910127", level: "alert", cause: "Usage above specified rate" },
    { name: "aws", time: "1723910032", level: "alert", cause: "Out of specified range" },
  ],
};

function getBadgeProps(level: ReportLevel) {
  switch (level) {
    case "warning":
      return { className: "bg-yellow-100 text-yellow-800", text: "Warning", icon: "Warning" };
    case "alert":
      return { className: "bg-red-100 text-red-800", text: "Alert", icon: "Alert" };
    default:
      return { className: "bg-gray-100 text-gray-800", text: "Unknown", icon: "Unknown" };
  }
}

export function Reports() {
  const uniqueServices = Array.from(new Set(Object.values(data).flat().map((item) => item.name)));

  const [filters, setFilters] = React.useState<Record<ReportLevel, boolean>>({
    warning: true,
    alert: true,
  });

  const [serviceFilters, setServiceFilters] = React.useState<Record<string, boolean>>(
    uniqueServices.reduce((accumulator, service) => {
      accumulator[service] = true;
      return accumulator;
    }, {} as Record<string, boolean>),
  );

  const handleFilterChange = (filterType: ReportLevel) => {
    setFilters((previousFilters) => ({
      ...previousFilters,
      [filterType]: !previousFilters[filterType],
    }));
  };

  const handleServiceFilterChange = (serviceName: string) => {
    setServiceFilters((previousServiceFilters) => ({
      ...previousServiceFilters,
      [serviceName]: !previousServiceFilters[serviceName],
    }));
  };

  const filteredData = Object.values(data)
    .flat()
    .filter((item) => filters[item.level] && serviceFilters[item.name]);

  return (
    <div className="w-full min-h-screen bg-muted/40 flex flex-col">
      <header className="bg-background border-b flex items-center h-16 px-4 shrink-0 md:px-6">
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-semibold sm:text-base mr-4"
          prefetch={false}
        >
          <svg
            className="w-6 h-6"
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
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
          </svg>
          <span>Cloud Anomalies</span>
        </Link>
        <div className="ml-auto flex items-center gap-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="bg-background">
                Filter{" "}
                <svg
                  className="ml-2 h-4 w-4"
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
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuCheckboxItem
                checked={filters.warning}
                onCheckedChange={() => handleFilterChange("warning")}
              >
                Warnings
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={filters.alert}
                onCheckedChange={() => handleFilterChange("alert")}
              >
                Alerts
              </DropdownMenuCheckboxItem>
              <DropdownMenuSeparator />
              {uniqueServices.map((service) => (
                <DropdownMenuCheckboxItem
                  key={service}
                  checked={serviceFilters[service]}
                  onCheckedChange={() => handleServiceFilterChange(service)}
                >
                  {service.charAt(0).toUpperCase() + service.slice(1)}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      <main className="flex-1 p-4 md:p-10">
        <div className="max-w-6xl w-full mx-auto">
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map((item, index) => {
                  const { className, text, icon } = getBadgeProps(item.level);

                  return (
                    <TableRow key={index}>
                      <TableCell>
                        <Badge variant="outline" className={className}>
                          {icon} {text}
                        </Badge>
                      </TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span>{icon}</span>
                          <span>{item.cause}</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Reports;
