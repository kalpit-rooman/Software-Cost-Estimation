import type { Metadata } from "next";
import EstimationFlow from "@/components/EstimationFlow";

export const metadata: Metadata = {
  title: "Estimate Software Cost",
  description:
    "Pick your project type and get a software development effort and cost estimate powered by ML models trained on COCOMO-81, Desharnais, and China datasets.",
};

export default function EstimatePage() {
  return <EstimationFlow />;
}
