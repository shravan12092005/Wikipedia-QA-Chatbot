import { createFileRoute } from "@tanstack/react-router";
import { SettingsPage } from "@/account/SettingsPage";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Account Settings — Wikipedia Research Assistant" },
      { name: "description", content: "Manage your profile details and account settings." },
    ],
  }),
  component: SettingsPage,
});
