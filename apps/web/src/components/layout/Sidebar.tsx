"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Map,
  Eye,
  Zap,
  TrendingUp,
  Settings,
  LogOut,
} from "lucide-react";

const links = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/farm-map", icon: Map, label: "Farm Map" },
  { href: "/detections", icon: Eye, label: "Detections" },
  { href: "/robotics", icon: Zap, label: "Robotics" },
  { href: "/predictions", icon: TrendingUp, label: "Predictions" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar(): JSX.Element {
  const pathname = usePathname();

  return (
    <div className="flex w-64 flex-col border-r border-border bg-card">
      <div className="border-b border-border p-6">
        <h1 className="text-xl font-bold">AgroMind</h1>
        <p className="text-xs text-muted-foreground">Agriculture Intelligence</p>
      </div>

      <nav className="flex-1 space-y-2 p-4">
        {links.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-4 py-2 text-sm transition-colors",
              pathname === href
                ? "bg-primary text-primary-foreground"
                : "text-foreground hover:bg-muted"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>

      <div className="border-t border-border p-4">
        <button
          className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm text-foreground hover:bg-muted"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
