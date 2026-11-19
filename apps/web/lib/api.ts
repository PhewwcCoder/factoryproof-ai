export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { ...options, headers: { ...(options?.body instanceof FormData ? {} : {'Content-Type': 'application/json'}), ...options?.headers }, credentials: 'same-origin' });
  if (!response.ok) {
    const body = await response.json().catch(() => ({detail: 'The service is unavailable. Please retry.'})) as {detail?:string};
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Check the form values and try again.');
  }
  return response.json();
}
