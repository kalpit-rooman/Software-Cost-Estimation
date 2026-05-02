"use client";

import type { ComponentType } from "react";

type IconProps = {
  size?: number;
  weight?: "regular" | "duotone" | "fill" | "light" | "thin" | "bold";
  className?: string;
};

type InputCardProps = {
  title: string;
  description: string;
  selected: boolean;
  onClick: () => void;
  icon: ComponentType<IconProps>;
};

export default function InputCard({ title, description, selected, onClick, icon: Icon }: InputCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "w-full rounded-2xl border p-5 text-left shadow-sm transition-all duration-200",
        selected
          ? "border-primary bg-primary/5"
          : "border-line/60 bg-card hover:border-primary/40",
      ].join(" ")}
    >
      <div className="flex items-start gap-4">
        <span
          className={[
            "mt-0.5 inline-flex h-10 w-10 items-center justify-center rounded-xl",
            selected ? "bg-primary/15 text-primary" : "bg-background text-muted",
          ].join(" ")}
        >
          <Icon size={20} weight="duotone" />
        </span>
        <span className="block">
          <span className="block text-base font-semibold text-foreground">{title}</span>
          <span className="mt-1 block text-sm leading-6 text-muted">{description}</span>
        </span>
      </div>
    </button>
  );
}
