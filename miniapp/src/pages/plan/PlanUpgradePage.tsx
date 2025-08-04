import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Check, Loader2 } from "lucide-react";
import { navigationStore } from "@/stores/NavigationStore";
import { getInvoiceLink } from "@/api/payments";
import { openInvoice } from "@telegram-apps/sdk";
import { getSubscriptionPlan, usePlans } from "@/api/plans";
import { useQueryClient } from "@tanstack/react-query";

export function PlanUpgradePage() {
  const queryClient = useQueryClient();
  const { data } = usePlans();
  const { t } = useTranslation("planUpgrade");
  const [selected, setSelected] = useState<string>(data.at(-1)?.id ?? "");
  const [loading, setLoading] = useState(false);

  const handleSelect = (id: string) => {
    setSelected(id);
  };

  const handleUpgrade = useCallback(async () => {
    setLoading(true);
    try {
      const { link } = await getInvoiceLink(selected);
      const status = await openInvoice(link, "url");
      console.log("payment status", status);
      if (status === "paid") {
        let subscription = await getSubscriptionPlan();
        while (subscription.plan === "free") {
          console.log("polling subscription");
          await new Promise((resolve) => setTimeout(resolve, 1000));
          subscription = await getSubscriptionPlan();
        }
        queryClient.invalidateQueries({ queryKey: ["subscription"] });
        navigationStore.setScreen("settings");
      }
    } catch (error) {
      console.error("upgrade error", error);
    } finally {
      setLoading(false);
    }
  }, [queryClient, selected]);

  return (
    <div className="p-4 space-y-6">
      <div className="space-y-3">
        {data.map((plan) => (
          <button
            key={plan.id}
            onClick={() => handleSelect(plan.id)}
            className={
              "flex flex-col cursor-pointer text-left w-full border rounded-2xl p-4 bg-background/60 backdrop-blur-sm transition-colors " +
              (selected === plan.id ? "border-primary" : "border-border")
            }
          >
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-muted-foreground">
                {plan.title}
                {plan.wishes > 0 && ` & +${plan.wishes} ✨`}
              </div>
              {selected === plan.id && (
                <span className="text-primary">
                  <Check className="w-5 h-5" />
                </span>
              )}
            </div>
            <div className="text-2xl font-bold text-foreground mt-1">
              {plan.is_promo ? (
                <>
                  {plan.old_price && (
                    <span className="mr-2 line-through text-muted-foreground">
                      ${plan.old_price}
                    </span>
                  )}{" "}
                  <span className="text-primary">${plan.price}</span>
                </>
              ) : (
                <span>${plan.price}</span>
              )}{" "}
              <span className="text-base font-normal">/ {plan.period}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Benefits */}
      <ul className="space-y-2 text-sm mt-4">
        <li className="flex items-center gap-2">
          <span className="text-primary">⚡</span>
          {t("infiniteEnergy")}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">✨</span>
          {t("wishesForShopping", {
            count: data.find((plan) => plan.id === selected)?.wishes ?? 0,
          })}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">🤖</span>
          {t("mostAdvancedAI")}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">🖼️</span>
          {t("unlimitedPhotoGeneration")}
        </li>
        {/* <li className="flex items-center gap-2">
          <span className="text-primary">💬</span>
          {t("nearInstantReplyTimes")}
        </li> */}
      </ul>

      <Button
        className="w-full h-12"
        onClick={handleUpgrade}
        disabled={loading}
      >
        {loading ? (
          <Loader2 className="w-8 h-8 animate-spin" />
        ) : (
          <>{t("upgrade")} ✨</>
        )}
      </Button>
    </div>
  );
}
