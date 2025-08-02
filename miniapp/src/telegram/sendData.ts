export async function sendDataToBot(data: unknown) {
    await window.Telegram?.WebApp.sendData(JSON.stringify(data));
}