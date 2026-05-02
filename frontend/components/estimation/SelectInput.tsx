"use client";

import type { ComponentType } from "react";

type IconProps = {
  size?: number;
  weight?: "regular" | "duotone" | "fill" | "light" | "thin" | "bold";
  className?: string;
};

type SelectOption = {
  value: string;
  label: string;
};

type SelectInputProps = {
  label: string;
  helperText: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  icon: ComponentType<IconProps>;
};

export default function SelectInput({
  label,
  helperText,
  value,
  options,
  onChange,
  icon: Icon,
}: SelectInputProps) {
  return (
    <label className="block rounded-2xl border border-line/60 bg-card p-5 shadow-sm">
      <div className="mb-3 flex items-start gap-3">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-background text-muted">
          <Icon size={18} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">{label}</p>
          <p className="text-xs text-muted">{helperText}</p>
        </div>
      </div>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="input-field text-sm"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
