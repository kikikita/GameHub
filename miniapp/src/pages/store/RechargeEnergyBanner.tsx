import { useTranslation } from "react-i18next";
import { Zap } from "lucide-react";
import { navigationStore } from "@/stores/NavigationStore";

export function RechargeEnergyBanner() {
  const { t } = useTranslation();

  const handleUnlimitedEnergy = () => {
    navigationStore.setScreen("plan");
  };
  return (
    <button
      onClick={handleUnlimitedEnergy}
      className="relative w-full overflow-hidden rounded-2xl bg-gradient-to-br from-primary/60 to-violet-600/60 p-4 text-left shadow-lg hover:brightness-105 transition-all cursor-pointer"
    >
      <div className="flex items-center gap-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-xl bg-black/20">
          <Zap className="h-10 w-10 text-yellow-400" />
        </div>
        <div className="flex-1 space-y-1">
          <h2 className="text-lg font-semibold text-white">
            {t("store:unlimitedEnergy", { defaultValue: "Unlimited Energy" })}
          </h2>
          <p className="text-sm text-white/80">
            {t("store:unlimitedEnergyDescription", {
              defaultValue: "Remove the barriers. Gain endless energy!",
            })}
          </p>
        </div>
      </div>
      <div className="mt-4">
        <span className="w-full inline-block rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium text-white backdrop-blur-sm text-center">
          {t("store:recharge", { defaultValue: "Recharge" })}
        </span>
      </div>
    </button>
  );
}
