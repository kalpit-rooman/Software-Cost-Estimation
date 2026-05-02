"use client";

import { ChartLine, Database, Sliders } from "@phosphor-icons/react";

import InputCard from "@/components/estimation/InputCard";
import type { ProjectType } from "@/components/estimation/types";

type Step1ProjectTypeProps = {
  options: ProjectType[];
  selectedId: ProjectType["id"] | null;
  onSelect: (id: ProjectType["id"]) => void;
};

const ICON_BY_ID = {
  "large-code-system": Database,
  "business-application": ChartLine,
  "medium-enterprise-system": Sliders,
};

export default function Step1ProjectType({ options, selectedId, onSelect }: Step1ProjectTypeProps) {
  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Project Type</h2>
        <p className="mt-2 text-sm text-muted">Choose the option that best matches your product.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {options.map((option) => {
          const Icon = ICON_BY_ID[option.id];
          return (
            <InputCard
              key={option.id}
              title={option.title}
              description={option.description}
              selected={selectedId === option.id}
              onClick={() => onSelect(option.id)}
              icon={Icon}
            />
          );
        })}
      </div>
    </div>
  );
}
