"use client";

import { Brain, Database, Sliders } from "@phosphor-icons/react";

import SliderInput from "@/components/estimation/SliderInput";
import type { CoreInputs } from "@/components/estimation/types";

type Step2CoreInputsProps = {
  values: CoreInputs;
  onChange: (values: CoreInputs) => void;
};

export default function Step2CoreInputs({ values, onChange }: Step2CoreInputsProps) {
  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Core Inputs</h2>
        <p className="mt-2 text-sm text-muted">Set three simple inputs to define overall project scope.</p>
      </div>

      <div className="space-y-4">
        <SliderInput
          label="Project Size"
          helperText="Approximate product scope and feature breadth."
          min={20}
          max={300}
          step={5}
          value={values.projectSize}
          onChange={(projectSize) => onChange({ ...values, projectSize })}
          icon={Database}
        />
        <SliderInput
          label="Team Experience"
          helperText="Average practical experience level of your delivery team."
          min={1}
          max={10}
          value={values.teamExperience}
          onChange={(teamExperience) => onChange({ ...values, teamExperience })}
          icon={Brain}
        />
        <SliderInput
          label="Complexity"
          helperText="How difficult architecture, integrations, and workflows are."
          min={1}
          max={10}
          value={values.complexity}
          onChange={(complexity) => onChange({ ...values, complexity })}
          icon={Sliders}
        />
      </div>
    </div>
  );
}
