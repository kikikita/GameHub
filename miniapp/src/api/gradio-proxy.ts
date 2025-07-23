import { getInitData } from "../telegram/init";
import { API_URL } from "./common";

export function makeGradioProxyRequest() { 
    return fetch(`${API_URL}/gradio/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `tma ${getInitData()}`,
        },
    });
}