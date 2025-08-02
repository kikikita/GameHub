
import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";
import { useSuspenseQuery } from "@tanstack/react-query";

interface Plan {
  id: string;
  title: string;
  price: number;
  currency: string;
  period: string;
  wishes: number;
  is_promo: boolean;
  old_price?: number;
}

export function getSubscriptionPlan(): Promise<{ plan: 'free' | 'pro' }> {
  return fetch(`${API_URL}/api/v1/subscription/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      'Authorization': `tma ${getInitData()}`,
    },
  }).then(res => res.json())
}

export function useSubscriptionPlan() {
  return useSuspenseQuery({
    queryKey: ["subscription"],
    queryFn: getSubscriptionPlan,
  });
}

export function getPlans(): Promise<Plan[]> {
  return fetch(`${API_URL}/api/v1/plans/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      'Authorization': `tma ${getInitData()}`,
    },
  }).then(res => res.json())
}

export function usePlans() {
  return useSuspenseQuery({
    queryKey: ["plans"],
    queryFn: getPlans,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  });
}