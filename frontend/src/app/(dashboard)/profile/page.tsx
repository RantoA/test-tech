"use client";

import { PageHeader } from "@/components/layout/PageHeader";
import { PasswordForm } from "@/components/profile/PasswordForm";
import { ProfileForm } from "@/components/profile/ProfileForm";
import { useAuth } from "@/hooks/useAuth";
import { formatDate } from "@/utils/format";

function Section({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="grid gap-6 border-b border-line py-8 md:grid-cols-[260px_minmax(0,1fr)]">
      <div>
        <h2 className="text-base font-semibold text-ink">{title}</h2>
        <p className="mt-1 text-sm text-muted">{description}</p>
      </div>
      <div className="max-w-xl border border-line bg-surface p-6">{children}</div>
    </section>
  );
}

export default function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div>
      <PageHeader title="Profile" description={`Member since ${formatDate(user.created_at)}`} />
      <Section title="Account information" description="Your name is displayed as the author of your articles.">
        <ProfileForm key={user.updated_at} user={user} />
      </Section>
      <Section title="Password" description="Use a strong password that you do not use elsewhere.">
        <PasswordForm />
      </Section>
    </div>
  );
}
