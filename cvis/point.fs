#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;
in vec2 fragTexCoord2;
in vec3 fragPosition;
in vec4 fragColor;
in vec3 fragNormal;
in vec4 screen_pos;
in vec4 center_screen_pos;

// Input uniform values
// uniform vec4 point_colors[];

// Output fragment color
out vec4 finalColor;

void main()
{
    // Texel color fetching from texture sampler
    // vec4 texelColor = texture(texture0, fragTexCoord);
    // vec4 texelColor2 = texture(texture1, fragTexCoord2);

    // finalColor.rgb = fragColor.rgb * dot(fragNormal,normalize(vec3(1,1,1)));
    // finalColor.a = 1.0;
    finalColor = fragColor;
    // finalColor = vec4(1);
    // finalColor = point_colors[gl_InstanceID];
    // finalColor.a /= 1000.0*distance(screen_pos.xy, center_screen_pos.xy);
    // finalColor.rg *= screen_pos.xy;
}