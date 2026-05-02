import type { DatasetKey } from "@/lib/api";

export type ProjectType = {
  id: "large-code-system" | "business-application" | "medium-enterprise-system";
  title: string;
  description: string;
  dataset: DatasetKey;
};

export type CoreInputs = {
  projectSize: number;
  teamExperience: number;
  complexity: number;
};

export type ReliabilityOption = "low" | "medium" | "high";
export type DataIntensityOption = "low" | "medium" | "high";
export type TeamFamiliarityOption = "new" | "some_experience" | "expert";
export type TimeConstraintOption = "flexible" | "moderate" | "tight";
export type ToolingMaturityOption = "experimental" | "stable" | "optimized";

export type AdvancedInputs = {
  reliabilityRequirement: ReliabilityOption;
  dataIntensity: DataIntensityOption;
  teamFamiliarity: TeamFamiliarityOption;
  timeConstraint: TimeConstraintOption;
  toolingMaturity: ToolingMaturityOption;
  techStack: import("@/lib/api").TechStack;
  monthlySalary: number;
  useTeamComposition: boolean;
  teamRoles: { id: string; role_name: string; percentage: number; monthly_rate_inr: number }[];
};
