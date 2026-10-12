"use client";

import { useState } from "react";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";

export default function AdminPage() {
  const [stats] = useState({ users: 0, valuations: 0, methods: 68, benchmarks: 27 });

  return (
    <div className="container-page py-8">
      <div className="flex gap-8">
        <DashboardSidebar />
        <div className="flex-1 min-w-0">
          <h1 className="text-display-sm text-primary-500 mb-2">Admin Panel</h1>
          <p className="text-neutral-500 mb-8">Platform management, user administration, and system health.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Registered Users", value: stats.users, unit: "" },
              { label: "Total Valuations", value: stats.valuations, unit: "" },
              { label: "Valuation Methods", value: stats.methods, unit: "" },
              { label: "Benchmark Records", value: stats.benchmarks, unit: "" },
            ].map((stat) => (
              <div key={stat.label} className="card p-5">
                <p className="text-xs font-semibold text-neutral-400 uppercase mb-2">{stat.label}</p>
                <p className="text-3xl font-bold font-mono text-primary-500">
                  {stat.value.toLocaleString()}{stat.unit}
                </p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-6">
              <h2 className="font-serif font-semibold text-neutral-900 dark:text-white mb-4">User Management</h2>
              <p className="text-sm text-neutral-500 mb-4">View and manage user roles, subscriptions, and activity.</p>
              <div className="space-y-2">
                {["public", "auditor", "admin"].map((role) => (
                  <div key={role} className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 dark:bg-neutral-900">
                    <span className="text-sm font-medium capitalize">{role}</span>
                    <span className="text-xs text-neutral-400">Manage role permissions via SurrealDB or provider dashboard</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-6">
              <h2 className="font-serif font-semibold text-neutral-900 dark:text-white mb-4">System Health</h2>
              <div className="space-y-4">
                {[
                  { service: "SurrealDB", status: "Checking..." },
                  { service: "Vercel Python API", status: "Checking..." },
                  { service: "NextAuth.js", status: "Active" },
                  { service: "MCP Gateway", status: "Active" },
                ].map((svc) => (
                  <div key={svc.service} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600 dark:text-neutral-400">{svc.service}</span>
                    <span className="text-xs font-medium text-green-600 bg-green-50 dark:bg-green-950 px-2 py-0.5 rounded-full">
                      {svc.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-6">
              <h2 className="font-serif font-semibold text-neutral-900 dark:text-white mb-4">Seed Data Management</h2>
              <p className="text-sm text-neutral-500 mb-3">Manage method catalog and benchmark data.</p>
              <div className="flex gap-3">
                <button className="px-4 py-2 rounded-lg bg-primary-500 text-white text-sm font-medium hover:bg-primary-600">
                  Re-run Seed
                </button>
                <button className="px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800">
                  Export Benchmarks
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
