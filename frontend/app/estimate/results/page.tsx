import type { Metadata } from "next";
import ResultsPage from "@/components/ResultsPage";

export const metadata: Metadata = {
  title: "Estimation Results",
  description: "Your ML-powered software cost and effort estimate.",
};

export default function EstimateResultsPage() {
  return <ResultsPage />;
}
