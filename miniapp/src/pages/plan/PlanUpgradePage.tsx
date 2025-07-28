import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { navigationStore } from "@/stores/NavigationStore";

interface PlanOption {
  id: string;
  title: string;
  priceLabel: string;
  periodLabel: string;
  wishes: number;
}

const plans: PlanOption[] = [
  {
    id: "3days",
    title: "3 Days",
    priceLabel: "$0.99",
    periodLabel: "/ 3 days",
    wishes: 5,
  },
  {
    id: "month",
    title: "1 Month",
    priceLabel: "$6.90",
    periodLabel: "/ month",
    wishes: 30,
  },
  {
    id: "quarter",
    title: "3 Months",
    priceLabel: "$13.80",
    periodLabel: "/ 3 months",
    wishes: 70,
  },
  {
    id: "year",
    title: "1 Year",
    priceLabel: "$41.40",
    periodLabel: "/ year",
    wishes: 210,
  },
];

export function PlanUpgradePage() {
  const { t } = useTranslation('planUpgrade');
  const [selected, setSelected] = useState<string>("year");

  const handleSelect = (id: string) => {
    setSelected(id);
  };

  return (
    <div className="p-4 space-y-6">
      <div className="space-y-3">
        {plans.map((plan) => (
          <button
            key={plan.id}
            onClick={() => handleSelect(plan.id)}
            className={
              "flex flex-col cursor-pointer text-left w-full border rounded-2xl p-4 bg-background/60 backdrop-blur-sm transition-colors " +
              (selected === plan.id
                ? "border-primary"
                : "border-border")
            }
          >
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-muted-foreground">
                {plan.title} {plan.wishes > 0 && `+${plan.wishes} ✨`}
              </div>
              {selected === plan.id && (
                <span className="text-primary">
                  <Check className="w-5 h-5" />
                </span>
              )}
            </div>
            <div className="text-2xl font-bold text-foreground mt-1">
              {plan.priceLabel}{" "}
              <span className="text-base font-normal">{plan.periodLabel}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Benefits */}
      <ul className="space-y-2 text-sm mt-4">
        <li className="flex items-center gap-2">
          <span className="text-primary">⚡</span>
          {t('infiniteEnergy')}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">✨</span>
          {t('wishesForShopping', { count: plans.find((plan) => plan.id === selected)?.wishes ?? 0 })}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">🤖</span>
          {t('mostAdvancedAI')}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">🖼️</span>
          {t('unlimitedPhotoGeneration')}
        </li>
        <li className="flex items-center gap-2">
          <span className="text-primary">💬</span>
          {t('nearInstantReplyTimes')}
        </li>
      </ul>

      <Button
        className="w-full h-12"
        onClick={() => {
          navigationStore.setScreen("settings");
        }}
      >
        {t('upgrade')} ✨
      </Button>
    </div>
  );
}
