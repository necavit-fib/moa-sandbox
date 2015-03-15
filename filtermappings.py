filtersMap = {
	'differentialprivacy.DifferentialPrivacyFilter': 'dp',
	'microaggregation.MicroAggregationFilter': 'ma',
	'noiseaddition.NoiseAdditionFilter': 'na',
	'rankswapping.RankSwappingFilter': 'rs'
}

filtersInverseMap = {v: k for k, v in filtersMap.items()}

def getFilterCode(filterName):
	return filtersMap[filterName]

def getFilterName(filterCode):
	return filtersInverseMap[filterCode].split('.')[1]

def getFullyQualifiedFilterName(filterCode):
	return filtersInverseMap[filterCode]
