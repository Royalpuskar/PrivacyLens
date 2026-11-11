"""Map user-described data exposure and prioritize privacy hygiene."""
import json

WEIGHTS={'contact':1,'location':3,'financial':4,'health':4,'identity':5,'preferences':1}
def analyze(data):
    results=[]
    for service in data.get('services',[]):
        categories=set(service.get('categories',[]))
        unknown=sorted(categories-WEIGHTS.keys())
        if unknown: raise ValueError('Unknown data category: '+', '.join(unknown))
        if service.get('retention_days',0)<0: raise ValueError('Retention cannot be negative')
        score=sum(WEIGHTS[x] for x in categories)
        reasons=[]
        if service.get('public',False): score*=2; reasons.append('Review publicly shared data')
        if not service.get('mfa',False): score+=3; reasons.append('Enable MFA if supported')
        if service.get('retention_days',0)>365: score+=2; reasons.append('Review long retention period')
        results.append({'service':service['name'],'exposure_index':score,'actions':reasons,'categories':sorted(categories)})
    return {'services':sorted(results,key=lambda r:(-r['exposure_index'],r['service'])),'basis':'user-supplied inventory; illustrative weights'}

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Path to a JSON scenario')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError('Input must be a JSON object')
        print(json.dumps(analyze(data), indent=2, sort_keys=True))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print('Input error: '+str(error), file=sys.stderr)
        sys.exit(2)
