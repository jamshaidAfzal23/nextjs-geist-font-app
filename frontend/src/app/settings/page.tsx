import { SettingsForm } from "@/components/settings/settings-form";
import { DashboardShell } from "@/components/shell";
import { DashboardHeader } from "@/components/header";

export default function SettingsPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Settings"
        text="Manage application settings and configurations"
      />
      <div className="grid gap-10">
        <SettingsForm />
      </div>
    </DashboardShell>
  );
}