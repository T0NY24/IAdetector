export async function askDeepSeek(prompt) {
    const res = await fetch("/api/semantic/deepseek", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
    });

    return await res.json();
}
