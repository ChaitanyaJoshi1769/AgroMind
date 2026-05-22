"use client";

import React from "react";
import { OperationsDashboard } from "@/components/dashboard/OperationsDashboard";

export default function HomePage(): JSX.Element {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Operations Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time monitoring and control of your agricultural operations
        </p>
      </div>
      <OperationsDashboard />
    </div>
  );
}
