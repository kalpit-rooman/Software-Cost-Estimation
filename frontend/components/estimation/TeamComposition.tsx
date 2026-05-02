"use client";

import { Plus, Trash, Users } from "@phosphor-icons/react";
import type { AdvancedInputs } from "./types";

type TeamCompositionProps = {
  values: AdvancedInputs;
  onChange: (values: AdvancedInputs) => void;
};

const TEMPLATES = [
  {
    name: "Standard Team",
    roles: [
      { id: "1", role_name: "Senior Developer", percentage: 20, monthly_rate_inr: 250000 },
      { id: "2", role_name: "Mid Developer", percentage: 40, monthly_rate_inr: 150000 },
      { id: "3", role_name: "Junior Developer", percentage: 20, monthly_rate_inr: 80000 },
      { id: "4", role_name: "QA Engineer", percentage: 10, monthly_rate_inr: 100000 },
      { id: "5", role_name: "Project Manager", percentage: 10, monthly_rate_inr: 200000 },
    ],
  },
  {
    name: "Enterprise Team",
    roles: [
      { id: "1", role_name: "Architect", percentage: 10, monthly_rate_inr: 350000 },
      { id: "2", role_name: "Senior Developer", percentage: 30, monthly_rate_inr: 250000 },
      { id: "3", role_name: "Mid Developer", percentage: 40, monthly_rate_inr: 150000 },
      { id: "4", role_name: "QA Automation", percentage: 15, monthly_rate_inr: 180000 },
      { id: "5", role_name: "Product Manager", percentage: 5, monthly_rate_inr: 300000 },
    ],
  },
];

export default function TeamComposition({ values, onChange }: TeamCompositionProps) {
  const roles = values.teamRoles;
  const totalPercentage = roles.reduce((sum, role) => sum + role.percentage, 0);

  const handleAddRole = () => {
    onChange({
      ...values,
      teamRoles: [
        ...roles,
        { id: Math.random().toString(), role_name: "New Role", percentage: 0, monthly_rate_inr: 100000 },
      ],
    });
  };

  const handleUpdateRole = (id: string, field: string, value: string | number) => {
    onChange({
      ...values,
      teamRoles: roles.map((role) =>
        role.id === id ? { ...role, [field]: value } : role
      ),
    });
  };

  const handleRemoveRole = (id: string) => {
    onChange({
      ...values,
      teamRoles: roles.filter((role) => role.id !== id),
    });
  };

  const applyTemplate = (templateRoles: typeof roles) => {
    onChange({
      ...values,
      teamRoles: templateRoles.map(r => ({ ...r, id: Math.random().toString() })),
    });
  };

  return (
    <div className="space-y-4 rounded-2xl border border-line/60 bg-card p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="inline-flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-background text-muted">
            <Users size={18} weight="duotone" />
          </span>
          <div>
            <p className="text-sm font-semibold text-foreground">Team Role Breakdown</p>
            <p className="text-xs text-muted">Define the specific roles to calculate a blended cost rate.</p>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {TEMPLATES.map((tpl) => (
          <button
            key={tpl.name}
            type="button"
            onClick={() => applyTemplate(tpl.roles)}
            className="whitespace-nowrap rounded-lg border border-line bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted/10"
          >
            Load {tpl.name}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {roles.map((role) => (
          <div key={role.id} className="flex items-center gap-2">
            <input
              type="text"
              value={role.role_name}
              onChange={(e) => handleUpdateRole(role.id, "role_name", e.target.value)}
              className="w-1/3 rounded-lg border border-line bg-background px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="Role Name"
            />
            <div className="flex w-1/4 items-center rounded-lg border border-line bg-background px-3 py-2">
              <input
                type="number"
                value={role.percentage}
                onChange={(e) => handleUpdateRole(role.id, "percentage", Number(e.target.value))}
                className="w-full bg-transparent text-sm text-foreground focus:outline-none"
                min="0"
                max="100"
              />
              <span className="text-xs text-muted">%</span>
            </div>
            <div className="flex flex-1 items-center rounded-lg border border-line bg-background px-3 py-2">
              <span className="text-xs text-muted mr-1">₹</span>
              <input
                type="number"
                value={role.monthly_rate_inr}
                onChange={(e) => handleUpdateRole(role.id, "monthly_rate_inr", Number(e.target.value))}
                className="w-full bg-transparent text-sm text-foreground focus:outline-none"
                step="10000"
              />
            </div>
            <button
              type="button"
              onClick={() => handleRemoveRole(role.id)}
              className="flex-shrink-0 p-2 text-muted hover:text-rose-500"
            >
              <Trash size={18} />
            </button>
          </div>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-line/40 pt-4">
        <button
          type="button"
          onClick={handleAddRole}
          className="flex items-center gap-1.5 rounded-lg bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted/10 border border-line"
        >
          <Plus size={14} /> Add Role
        </button>
        
        <div className={`text-sm font-semibold ${totalPercentage === 100 ? "text-emerald-600" : "text-amber-600"}`}>
          Total: {totalPercentage}% {totalPercentage !== 100 && "(Must equal 100%)"}
        </div>
      </div>
    </div>
  );
}
