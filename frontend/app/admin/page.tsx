import type { Metadata } from "next";
import AdminDashboard from "@/components/AdminDashboard";

export const metadata: Metadata = {
  title: "Admin",
  description: "Runtime configuration dashboard for SoftEstimate.",
};

export default function AdminPage() {
  return <AdminDashboard />;
}
