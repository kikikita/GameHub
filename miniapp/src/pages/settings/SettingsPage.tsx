import { useSubscriptionPlan } from "@/api/plans";
import { useUpdateUser, useUser } from "@/api/user";
import { Button } from "@/components/ui/button";
import { navigationStore } from "@/stores/NavigationStore";
import { useTranslation } from "react-i18next";
import { LanguageSelector } from "./LanguageSelector";
import { ImageFormatSelector } from "./ImageFormatSelector";

export type Plan = "free" | "pro";

export function SettingsPage() {
  const { t } = useTranslation('settings');
  const { data: { plan } } = useSubscriptionPlan();
  const { data: { language, image_format } } = useUser();
  const { mutate: updateUser } = useUpdateUser();

  return (
    <div className="p-4 space-y-6">
      <section className="bg-background/60 backdrop-blur-sm border border-border rounded-2xl p-4 space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground">{t("yourPlan")}</h3>
        <div className="text-4xl font-bold text-foreground capitalize">{t(plan)}</div>
        {plan === "free" && (
          <Button
            className="w-full"
            onClick={() => {
              navigationStore.setScreen("plan");
            }}
          >
            {t("upgrade")}
          </Button>
        )}
      </section>

      <section className="bg-background/60 backdrop-blur-sm border border-border rounded-2xl">
        <LanguageSelector
          value={language}
          onChange={(code) => {
            updateUser({ language: code });
          }}
        />
      </section>

      <section className="bg-background/60 backdrop-blur-sm border border-border rounded-2xl">
        <ImageFormatSelector
          value={image_format}
          onChange={(format) => {
            updateUser({ image_format: format as "vertical" | "horizontal" });
          }}
        />
      </section>
    </div>
  );
}