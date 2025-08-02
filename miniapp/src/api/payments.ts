import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";

interface InvoiceResponse {
  link: string;
}

export function getInvoiceLink(plan: string): Promise<InvoiceResponse> {
  return fetch(`${API_URL}/api/v1/subscribe/?plan=${plan}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      'Authorization': `tma ${getInitData()}`,
    },
  }).then(res => res.json())
}