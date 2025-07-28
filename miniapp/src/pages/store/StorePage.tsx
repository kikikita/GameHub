import { navigationStore } from "@/stores/NavigationStore";
import { useTranslation } from "react-i18next";
import { Star, Zap } from "lucide-react";

interface Pack {
  id: string;
  wishes: number;
  price: string;
}

const packs: Pack[] = [
  { id: "540", wishes: 540, price: "$38.00" },
  { id: "1360", wishes: 1360, price: "$79.00" },
  { id: "2720", wishes: 2720, price: "$141.00" },
  { id: "210", wishes: 210, price: "$18.00" },
  { id: "5000", wishes: 5000, price: "$200.00" },
  { id: "85", wishes: 85, price: "$8.80" },
];

export function StorePage() {
  const { t } = useTranslation();

  const handleUnlimitedEnergy = () => {
    navigationStore.setScreen("plan");
  };

  return (
    <div className="p-4 space-y-6 pb-20">
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
      <div className="grid grid-cols-2 gap-4">
        {packs.map((pack) => (
          <button
            key={pack.id}
            className="flex flex-col items-center justify-center gap-2 rounded-xl border border-border bg-background/60 backdrop-blur-sm p-4 hover:bg-background/80 transition-colors cursor-pointer"
            onClick={() => alert(`Pretend purchasing ${pack.wishes} wishes`)}
          >
            <Star className="h-8 w-8 text-primary" />
            <div className="text-primary font-medium text-sm">
              {pack.wishes} {t("store:wishes", { defaultValue: "Wishes" })}
            </div>
            <div className="text-foreground text-xs font-semibold">
              {pack.price}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
} 