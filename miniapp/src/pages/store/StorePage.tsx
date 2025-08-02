import { useTranslation } from "react-i18next";
import { Star } from "lucide-react";
import { useSubscriptionPlan } from "@/api/plans";
import { RechargeEnergyBanner } from "./RechargeEnergyBanner";

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
  const { data: { plan } } = useSubscriptionPlan();

  return (
    <div className="p-4 space-y-6 pb-20">
      {plan !== "pro" && <RechargeEnergyBanner />}
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