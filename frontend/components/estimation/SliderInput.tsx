"use client";

import type { ComponentType } from "react";

type IconProps = {
  size?: number;
  weight?: "regular" | "duotone" | "fill" | "light" | "thin" | "bold";
  className?: string;
};

type SliderInputProps = {
  label: string;
  helperText: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (value: number) => void;
  icon: ComponentType<IconProps>;
  formatValue?: (value: number) => string;
};

export default function SliderInput({
  label,
  helperText,
  min,
  max,
  step = 1,
  value,
  onChange,
  icon: Icon,
  formatValue,
}: SliderInputProps) {
  return (
    <div className="rounded-2xl border border-line/60 bg-card p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-background text-muted">
            <Icon size={18} weight="duotone" />
          </span>
          <div>
            <p className="text-sm font-semibold text-foreground">{label}</p>
            <p className="text-xs text-muted">{helperText}</p>
          </div>
        </div>
        <p className="rounded-lg bg-background px-2.5 py-1 text-xs font-semibold text-foreground">{formatValue ? formatValue(value) : value}</p>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer"
      />
      <div className="mt-2 flex justify-between text-[11px] text-muted">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
