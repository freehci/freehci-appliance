/** Åpner tjenestekatalogens deploy-fane med en enhet valgt. Installerer ikke OS. */
export function catalogProvisionHref(deviceId: number): string {
  return `/services?tab=deploy&device=${deviceId}`;
}
