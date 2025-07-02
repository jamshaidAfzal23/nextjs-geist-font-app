import { ProfileForm } from "@/components/profile/profile-form";
import { DashboardShell } from "@/components/shell";
import { DashboardHeader } from "@/components/header";

export default function ProfilePreferencesPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Preferences"
        text="Manage your account settings and preferences"
      />
      <div className="grid gap-10">
        <ProfileForm />
      </div>
    </DashboardShell>
  );
}