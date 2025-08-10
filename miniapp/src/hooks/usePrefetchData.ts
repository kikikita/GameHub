import { getBundles } from "@/api/payments";
import { getPlans, getSubscriptionPlan } from "@/api/plans";
import { getRealms, useRealms } from "@/api/realms";
import { getStories } from "@/api/stories";
import { getUser } from "@/api/user";
import { usePrefetchQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";

export function usePrefetchData() {

  const queryClient = useQueryClient();
  const { i18n } = useTranslation();

  usePrefetchQuery({
    queryKey: ["realms"],
    queryFn: () => window.prefetchedRealms ?? getRealms(i18n.language),
  });

  const { data: realms } = useRealms();

  useEffect(() => {
    if (realms) {
      const lang = i18n.language;
      realms.forEach((realm) => {
        queryClient.prefetchQuery({
          queryKey: ["stories", realm.id, lang],
          queryFn: () => getStories(realm.id, lang),
        });
      });
    }
  }, [queryClient, realms, i18n.language]);

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