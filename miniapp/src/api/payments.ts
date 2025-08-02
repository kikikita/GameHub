import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";
import { useSuspenseQuery } from "@tanstack/react-query";

interface InvoiceResponse {
  link: string;
}

/* -------------------- Subscriptions (existing) -------------------- */
export function getInvoiceLink(plan: string): Promise<InvoiceResponse> {
  return fetch(`${API_URL}/api/v1/subscribe/?plan=${plan}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `tma ${getInitData()}`,
    },
  }).then((res) => res.json());
}

export interface WishBundle {
  id: string;
  title: string;
  price: number;
  currency: string;
  stars: number;
  wishes: number;
  is_promo: boolean;
  old_price?: number;
  image_url?: string;
}

export function getBundles(): Promise<WishBundle[]> {
  return fetch(`${API_URL}/api/v1/wishes/bundles/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `tma ${getInitData()}`,
    },
  }).then((res) => res.json());
}

export function getWishInvoiceLink(bundle: string): Promise<InvoiceResponse> {
  return fetch(`${API_URL}/api/v1/wishes/buy/?bundle=${bundle}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `tma ${getInitData()}`,
    },
  }).then((res) => res.json());
}


export function useBundles() {
  return useSuspenseQuery({
    queryKey: ["wish-bundles"],
    queryFn: getBundles,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  });
}
