import { getBundles } from "@/api/payments";
import { getPlans, getSubscriptionPlan } from "@/api/plans";
import { getUser } from "@/api/user";
import { usePrefetchQuery } from "@tanstack/react-query";

export function usePrefetchData() {
  usePrefetchQuery({
    queryKey: ["plans"],
    queryFn: getPlans,
  });

  usePrefetchQuery({
    queryKey: ["subscription"],
    queryFn: getSubscriptionPlan,
  });

  usePrefetchQuery({
    queryKey: ["user"],
    queryFn: getUser,
  });

  usePrefetchQuery({
    queryKey: ["wish-bundles"],
    queryFn: getBundles,
  });
}