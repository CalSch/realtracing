#version 330

// Input vertex attributes
in vec3 vertexPosition;
in vec2 vertexTexCoord;
in vec3 vertexNormal;
//in vec4 vertexColor;      // Not required

in mat4 instanceTransform;

// Input uniform values
uniform mat4 mvp;
uniform mat4 matNormal;

// Output vertex attributes (to fragment shader)
out vec3 fragPosition;
out vec2 fragTexCoord;
out vec4 fragColor;
out vec3 fragNormal;
out vec4 screen_pos;
out vec4 center_screen_pos;

// NOTE: Add your custom variables here

void main()
{

    vec3 point_pos = instanceTransform[0].xyz;
    vec3 point_color = instanceTransform[1].rgb;

    // Transform only the instance center.
    vec4 centerClip =
        mvp * vec4(point_pos, 1.0);

    // Adjust this to control the apparent dot size.
    // This is in normalized screen-space units.
    const float dotSize = 0.01;

    // The triangle's local X/Y coordinates become screen-space offsets.
    // centerClip.w preserves roughly correct perspective behavior.
    vec2 screenOffset = vertexPosition.xz * dotSize * centerClip.w;

    gl_Position = centerClip;
    gl_Position.xy += screenOffset / centerClip.w;

    // These values are mainly useful if your fragment shader uses them.
    fragPosition = point_pos;

    fragTexCoord = vertexTexCoord;
    fragColor = vec4(point_color, 1.0);

    // A fixed normal is sufficient for unlit dots.
    fragNormal = vec3(0.0, 0.0, 1.0);

    screen_pos = gl_Position;
    center_screen_pos = centerClip;
}