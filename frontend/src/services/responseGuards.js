function hasKeys(object, keys) {
  return object && keys.every((key) => Object.prototype.hasOwnProperty.call(object, key))
}

export function validateUserPayload(payload) {
  if (!hasKeys(payload, ['id', 'name', 'email'])) {
    throw new Error('Unexpected user response from API.')
  }
  return payload
}

export function validateProfilePayload(payload) {
  if (!hasKeys(payload, ['user', 'analysis_count', 'average_monthly_emissions'])) {
    throw new Error('Unexpected profile response from API.')
  }
  return payload
}

export function validateAnalysisPayload(payload) {
  if (!hasKeys(payload, ['analysis', 'message'])) {
    throw new Error('Unexpected analysis response from API.')
  }
  return payload
}
