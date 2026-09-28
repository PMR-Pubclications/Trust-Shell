import sha256_pkg::*;

module sha256_round (
    input  logic [31:0] state_in[8], // {a, b, c, d, e, f, g, h}
    input  logic [31:0] w_i,         // Message schedule word
    input  logic [31:0] k_i,         // Round constant
    output logic [31:0] state_out[8]
);
    logic [31:0] a, b, c, d, e, f, g, h;
    assign {a, b, c, d, e, f, g, h} = state_in;

    // Intermediate CSA outputs to compress add operations without propagation delay
    logic [31:0] csa1_s, csa1_c;
    logic [31:0] csa2_s, csa2_c;
    logic [31:0] t1, t2;

    // Compress: h + S1(e) + Ch(e,f,g) + k_i + w_i
    csa_32 csa1 (
        .a(h),
        .b(S1(e)),
        .c(Ch(e, f, g)),
        .sum(csa1_s),
        .carry(csa1_c)
    );

    csa_32 csa2 (
        .a(csa1_s),
        .b(csa1_c << 1),
        .c(k_i + w_i),
        .sum(csa2_s),
        .carry(csa2_c)
    );

    // Final addition for Round T1 & T2
    assign t1 = csa2_s + (csa2_c << 1);
    assign t2 = S0(a) + Maj(a, b, c);

    // Register State Updates for next pipeline stage
    assign state_out[0] = t1 + t2; // new 'a'
    assign state_out[1] = a;        // new 'b'
    assign state_out[2] = b;        // new 'c'
    assign state_out[3] = c;        // new 'd'
    assign state_out[4] = d + t1;   // new 'e'
    assign state_out[5] = e;        // new 'f'
    assign state_out[6] = f;        // new 'g'
    assign state_out[7] = g;        // new 'h'

endmodule
