import { useTranslation } from "react-i18next";
import energyIcon from "@/assets/images/energy_icon.webp";
import { navigationStore } from "@/stores/NavigationStore";

export function RechargeEnergyBanner() {
  const { t } = useTranslation();

  const handleUnlimitedEnergy = () => {
    navigationStore.setScreen("plan");
  };
  return (
    <button
      onClick={handleUnlimitedEnergy}
      className="relative w-full overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500/60 via-purple-600/70 to-fuchsia-600/60 p-4 text-left shadow-lg hover:brightness-105 transition-all cursor-pointer"
    >
      <div className="flex items-center gap-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-xl bg-gradient-to-br from-purple-400/40 via-purple-500/50 to-purple-700/60 shadow-inner">
          <img src={energyIcon} alt="Energy Icon" className="h-16 w-16 object-contain" />
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
        <span className="w-full inline-block rounded-[22px] bg-gradient-to-r from-green-400 to-green-600 px-8 py-3 text-lg font-semibold text-white text-center shadow-md" style={{ border: "none" }}>
          {t("store:recharge", { defaultValue: "Recharge" })}
        </span>
      </div>
    </button>
  );
}
