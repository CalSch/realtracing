
// A single iteration of Bob Jenkins' One-At-A-Time hashing algorithm.
uint hash(uint x) {
	x += (x << 10u);
	x ^= (x >> 6u);
	x += (x << 3u);
	x ^= (x >> 11u);
	x += (x << 15u);
	return x;
}
// Compound versions of the hashing algorithm I whipped together.
uint hash(uvec2 v) {
	return hash(v.x ^ hash(v.y));
}
uint hash(uvec3 v) {
	return hash(v.x ^ hash(v.y) ^ hash(v.z));
}
uint hash(uvec4 v) {
	return hash(v.x ^ hash(v.y) ^ hash(v.z) ^ hash(v.w));
}

// Construct a float with half-open range [0:1] using low 23 bits.
// All zeroes yields 0.0, all ones yields the next smallest representable value below 1.0.
float floatConstruct(uint m) {
	const uint ieeeMantissa = 0x007FFFFFu; // binary32 mantissa bitmask
	const uint ieeeOne = 0x3F800000u; // 1.0 in IEEE binary32

	m &= ieeeMantissa; // Keep only mantissa bits (fractional part)
	m |= ieeeOne; // Add fractional part to 1.0

	float f = uintBitsToFloat(m); // Range [1:2]
	return f - 1.0; // Range [0:1]
}

// Pseudo-random value in half-open range [0:1].
float randomS(float x) {
	return floatConstruct(hash(floatBitsToUint(x)));
}
float randomS(vec2 v) {
	return floatConstruct(hash(floatBitsToUint(v)));
}
float randomS(vec3 v) {
	return floatConstruct(hash(floatBitsToUint(v)));
}
float randomS(vec4 v) {
	return floatConstruct(hash(floatBitsToUint(v)));
}

vec3 random3S(float x) {
	vec3 v = vec3(0, 0, 0);
	x = randomS(x);
	v.x = x;
	x = randomS(x);
	v.y = x;
	x = randomS(x);
	v.z = x;
	return v;
}



float rng_seed;

float random() {
	rng_seed = randomS(rng_seed);
	return rng_seed;
}
float random_norm_dist() {
	// Thanks to https://stackoverflow.com/a/6178290
    float theta = 2 * 3.1415926 * random();
    float rho = sqrt(-2 * log(random()));
    return rho * cos(theta);
}
vec3 random3() {
	return vec3(random(), random(), random());
}
vec3 random_dir() {
	return normalize(vec3(
		random_norm_dist(),
		random_norm_dist(),
		random_norm_dist()
	));
}
