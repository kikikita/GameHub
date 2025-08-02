import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { Loader2 } from "lucide-react";
import { useSubscriptionPlan } from "@/api/plans";
import { RechargeEnergyBanner } from "./RechargeEnergyBanner";
import { useBundles, getWishInvoiceLink } from "@/api/payments";
import { openInvoice } from "@telegram-apps/sdk";
import { useQueryClient } from "@tanstack/react-query";

export function StorePage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const {
    data: { plan },
  } = useSubscriptionPlan();
  const { data: bundles } = useBundles();

  const [loadingFor, setLoadingFor] = useState<string | null>(null);

  const handlePurchase = useCallback(
    async (bundleId: string) => {
      setLoadingFor(bundleId);
      try {
        const { link } = await getWishInvoiceLink(bundleId);
        const status = await openInvoice(link, "url");
        console.log("payment status", status);
        if (status === "paid") {
          // Ideally we would poll an endpoint to refresh the user's balance.
          // For now just invalidate resource queries if any.
          queryClient.invalidateQueries({ queryKey: ["user-resources"] });
          alert(
            t("store:purchaseSuccess", { defaultValue: "Purchase successful!" })
          );
        }
      } catch (error) {
        console.error("purchase error", error);
      } finally {
        setLoadingFor(null);
      }
    },
    [queryClient, t]
  );

  return (
    <div className="p-4 space-y-6 pb-20">
      {plan !== "pro" && <RechargeEnergyBanner />}
      <div className="grid grid-cols-2 gap-4">
        {bundles.map((bundle) => {
          const isLoading = loadingFor === bundle.id;
          return (
            <button
              key={bundle.id}
              className="relative flex flex-col items-center justify-center gap-2 rounded-xl border border-border bg-background/60 backdrop-blur-sm p-4 hover:bg-background/80 transition-colors cursor-pointer"
              onClick={() => handlePurchase(bundle.id)}
              disabled={!!loadingFor}
            >
              {isLoading && (
                <div className="absolute inset-0 z-20 flex items-center justify-center rounded-xl bg-background/70 backdrop-blur-s">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              )}
              <div className="relative w-full flex items-center justify-center">
                {/* shadow blur effect below image */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-3/5 h-3/5 rounded-full bg-yellow-400/40 blur-2xl" />
                </div>
                <img
                  src={bundle.image_url}
                  alt={bundle.title}
                  className="relative z-10 w-full object-contain min-h-36"
                  loading="lazy"
                />
              </div>
              <div className="text-primary font-medium text-sm">
                {bundle.wishes} {t("store:wishes", { defaultValue: "Wishes" })}
              </div>
              <div className="text-foreground text-xs font-semibold">
                {bundle.is_promo ? (
                  <>
                    {bundle.old_price && (
                      <span className="mr-1 line-through text-muted-foreground">
                        ${bundle.old_price}
                      </span>
                    )}
                    <span className="text-primary">${bundle.price}</span>
                  </>
                ) : (
                  <span>${bundle.price}</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
