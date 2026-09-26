#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;
in vec2 fragTexCoord2;
in vec3 fragPosition;
in vec4 fragColor;
in vec3 fragNormal;
in vec4 screen_pos;

// Input uniform values
uniform sampler2D texture0;
uniform sampler2D texture1;

// Output fragment color
out vec4 finalColor;

void main()
{
    // Texel color fetching from texture sampler
    // vec4 texelColor = texture(texture0, fragTexCoord);
    // vec4 texelColor2 = texture(texture1, fragTexCoord2);

    // finalColor.rgb = fragColor.rgb * dot(fragNormal,normalize(vec3(1,1,1)));
    // finalColor.a = 1.0;

    vec3 ambient = vec3(0.2,0.3,0.4);
    vec3 light = vec3(1.3,1.2,1.1);
    float atten = 0.9;

    vec3 normal = normalize(cross(dFdx(fragPosition), dFdy(fragPosition)));
    // finalColor = fragColor;
    finalColor = vec4(1,1,1,1);
    float light_fac = dot(normal, normalize(vec3(0,1,0) - fragPosition));
    light_fac *= pow(atten, distance(vec3(0,1,0), fragPosition));
    finalColor.rgb *= mix(ambient,light,light_fac);
    // finalColor.a /= 1000.0*distance(screen_pos.xy, center_screen_pos.xy);
    // finalColor.rg *= screen_pos.xy;
}