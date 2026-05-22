"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { AlertCircle, TrendingUp, Droplet, Leaf } from "lucide-react";

export function OperationsDashboard(): JSX.Element {
  const stats = [
    {
      label: "Total Farms",
      value: "12",
      icon: Leaf,
      trend: "+2 this month",
    },
    {
      label: "Active Fields",
      value: "48",
      icon: TrendingUp,
      trend: "+5 recently planted",
    },
    {
      label: "Detections",
      value: "324",
      icon: AlertCircle,
      trend: "12 alerts pending",
    },
    {
      label: "Water Saved",
      value: "45,230 L",
      icon: Droplet,
      trend: "+12% vs baseline",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon, trend }) => (
          <Card key={label} className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold">{value}</p>
                <p className="text-xs text-muted-foreground">{trend}</p>
              </div>
              <Icon className="h-8 w-8 text-primary opacity-50" />
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="col-span-2 p-6">
          <h3 className="mb-4 text-lg font-semibold">Recent Detections</h3>
          <div className="space-y-4">
            {[
              { type: "Weed Detected", location: "Field A1", time: "2 hours ago" },
              { type: "Pest Alert", location: "Field B2", time: "4 hours ago" },
              { type: "Disease Forecast", location: "Field C3", time: "6 hours ago" },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between border-b border-border pb-4 last:border-0">
                <div>
                  <p className="font-medium">{item.type}</p>
                  <p className="text-xs text-muted-foreground">{item.location}</p>
                </div>
                <p className="text-xs text-muted-foreground">{item.time}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">Fleet Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Drones Active</span>
              <span className="font-bold">4/6</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Robots Active</span>
              <span className="font-bold">3/3</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Sensors Online</span>
              <span className="font-bold">45/48</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
