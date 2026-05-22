"use client";

import React from "react";
import { Bell, Settings, User } from "lucide-react";

export function Header(): JSX.Element {
  return (
    <div className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
      <div className="flex-1">
        <h2 className="text-lg font-semibold">Operations</h2>
      </div>

      <div className="flex items-center gap-4">
        <button className="rounded-lg p-2 hover:bg-muted">
          <Bell className="h-5 w-5 text-foreground" />
        </button>
        <button className="rounded-lg p-2 hover:bg-muted">
          <Settings className="h-5 w-5 text-foreground" />
        </button>
        <button className="rounded-lg p-2 hover:bg-muted">
          <User className="h-5 w-5 text-foreground" />
        </button>
      </div>
    </div>
  );
}
