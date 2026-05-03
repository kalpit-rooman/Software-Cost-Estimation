"use client";

import { AppWindow, Clock, CurrencyInr, Database, Shield, Users, Wrench } from "@phosphor-icons/react";

import SelectInput from "@/components/estimation/SelectInput";
import SliderInput from "@/components/estimation/SliderInput";
import TeamComposition from "@/components/estimation/TeamComposition";
import type { AdvancedInputs } from "@/components/estimation/types";

type Step3AdvancedInputsProps = {
  showAdvanced: boolean;
  onToggleAdvanced: (enabled: boolean) => void;
  values: AdvancedInputs;
  onChange: (values: AdvancedInputs) => void;
};

export default function Step3AdvancedInputs({
  showAdvanced,
  onToggleAdvanced,
  values,
  onChange,
}: Step3AdvancedInputsProps) {
  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Advanced Inputs</h2>
        <p className="mt-2 text-sm text-muted">Optional settings for better estimate precision.</p>
      </div>

      <label className="flex cursor-pointer items-center justify-between rounded-2xl border border-line/60 bg-card px-5 py-4 shadow-sm">
        <div>
          <p className="text-sm font-semibold text-foreground">Show Advanced Inputs</p>
          <p className="text-xs text-muted">Turn this on to tune technical and team factors.</p>
        </div>
        <input
          type="checkbox"
          checked={showAdvanced}
          onChange={(event) => onToggleAdvanced(event.target.checked)}
          className="h-5 w-5 rounded border-line/60 text-primary focus:ring-primary/20"
        />
      </label>

      {showAdvanced && (
        <div className="space-y-5">
          <section className="space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted">Technical Factors</h3>
            <div className="space-y-3">
              <SelectInput
                label="Reliability Requirement"
                helperText="How critical is the system?"
                value={values.reliabilityRequirement}
                onChange={(reliabilityRequirement) => onChange({ ...values, reliabilityRequirement: reliabilityRequirement as AdvancedInputs["reliabilityRequirement"] })}
                options={[
                  { value: "low", label: "Low" },
                  { value: "medium", label: "Medium" },
                  { value: "high", label: "High" },
                ]}
                icon={Shield}
              />
              <SelectInput
                label="Data Intensity"
                helperText="How much data does the system handle?"
                value={values.dataIntensity}
                onChange={(dataIntensity) => onChange({ ...values, dataIntensity: dataIntensity as AdvancedInputs["dataIntensity"] })}
                options={[
                  { value: "low", label: "Low" },
                  { value: "medium", label: "Medium" },
                  { value: "high", label: "High" },
                ]}
                icon={Database}
              />
              <SelectInput
                label="Tooling Maturity"
                helperText="How mature are your tools and frameworks?"
                value={values.toolingMaturity}
                onChange={(toolingMaturity) => onChange({ ...values, toolingMaturity: toolingMaturity as AdvancedInputs["toolingMaturity"] })}
                options={[
                  { value: "experimental", label: "Experimental" },
                  { value: "stable", label: "Stable" },
                  { value: "optimized", label: "Optimized" },
                ]}
                icon={Wrench}
              />
              <SelectInput
                label="Technology Stack"
                helperText="Primary technology stack to be used."
                value={values.techStack}
                onChange={(techStack) => onChange({ ...values, techStack: techStack as AdvancedInputs["techStack"] })}
                options={[
                  { value: "web", label: "Web Application" },
                  { value: "mobile_cross", label: "Mobile (Cross-platform)" },
                  { value: "mobile_native", label: "Mobile (Native)" },
                  { value: "enterprise", label: "Enterprise System" },
                  { value: "ai_ml", label: "AI / ML Heavy" },
                  { value: "embedded", label: "Embedded / IoT" },
                ]}
                icon={AppWindow}
              />
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted">Team Factors</h3>
            <div className="space-y-3">
              <SelectInput
                label="Team Familiarity"
                helperText="How familiar is your team with this domain?"
                value={values.teamFamiliarity}
                onChange={(teamFamiliarity) => onChange({ ...values, teamFamiliarity: teamFamiliarity as AdvancedInputs["teamFamiliarity"] })}
                options={[
                  { value: "new", label: "New" },
                  { value: "some_experience", label: "Some Experience" },
                  { value: "expert", label: "Expert" },
                ]}
                icon={Users}
              />
              <SelectInput
                label="Time Constraint"
                helperText="How strict is the project deadline?"
                value={values.timeConstraint}
                onChange={(timeConstraint) => onChange({ ...values, timeConstraint: timeConstraint as AdvancedInputs["timeConstraint"] })}
                options={[
                  { value: "flexible", label: "Flexible" },
                  { value: "moderate", label: "Moderate" },
                  { value: "tight", label: "Tight" },
                ]}
                icon={Clock}
              />
            </div>
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted">Budget</h3>
            </div>

            <label className="flex cursor-pointer items-center justify-between rounded-xl border border-line/60 bg-background px-4 py-3">
              <div>
                <p className="text-sm font-semibold text-foreground">Include cost analysis</p>
                <p className="text-xs text-muted">Show estimated project cost alongside effort.</p>
              </div>
              <input
                type="checkbox"
                checked={values.includeCostAnalysis}
                onChange={(e) => onChange({ ...values, includeCostAnalysis: e.target.checked })}
                className="h-5 w-5 rounded border-line/60 text-primary focus:ring-primary/20"
              />
            </label>

            {values.includeCostAnalysis && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted">Configure team rates</p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={values.useTeamComposition}
                      onChange={(e) => onChange({ ...values, useTeamComposition: e.target.checked })}
                      className="rounded border-line/60 text-primary focus:ring-primary/20 h-4 w-4"
                    />
                    <span className="text-xs text-muted">Use role-based breakdown</span>
                  </label>
                </div>

                {values.useTeamComposition ? (
                  <TeamComposition values={values} onChange={onChange} />
                ) : (
                  <SliderInput
                    label="Monthly Salary per Developer"
                    helperText="Blended monthly CTC including benefits and overhead."
                    min={30000}
                    max={500000}
                    step={10000}
                    value={values.monthlySalary}
                    onChange={(monthlySalary) => onChange({ ...values, monthlySalary })}
                    icon={CurrencyInr}
                    formatValue={(v) =>
                      `₹${new Intl.NumberFormat("en-IN").format(v)}/mo`
                    }
                  />
                )}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
