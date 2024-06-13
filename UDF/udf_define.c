

#include "udf.h"

static real T_Max_GLO = 0.0;
static real T_Min_GLO = REAL_MAX;

/*DEFINE_ADJUST用于获取物体的最大或最小温度*/
DEFINE_ADJUST(m_temperature, d)
{
    Thread *t;
    cell_t c;
    real T_Min = REAL_MIN;
    real T_Max = 0.0;

    if(N_UDM < 1)
    {
        Message("\n NO UDM!");
        return;
    }

    thread_loop_c(t, d)
    {
        begin_c_loop(c, t)
        {
            real T = C_T(c, t);
            C_UDMI(c, t, 0) = T;
            if(T > T_Max)
            {
                T_Max = T;
            }
            if(T < T_Min)
            {
                T_Min = T;
            }
        }
        end_c_loop(c, t)
    }
    T_Max_GLO = T_Max;
    T_Min_GLO = T_Min;
    Message0("T_Max = %g, T_Min = %g\n", T_Max_GLO, T_Min_GLO);
}


/* 计算lambda */
DEFINE_PROPERTY(lambda_total, c, t)
{
    /* 定义lambda中的参数 */
    real n = 1.04533468;
    real sigma = 5.67e-8;
    
    real T_ref[] = {300, 320, 340, 360, 380, 400, 420, 440, 
                    460, 480, 500, 520, 540, 560, 580, 600,
                    620, 640, 660, 680, 700};
    real beta[] = {9533.88418051722, 8888.75251334191, 8215.39685682778, 7578.40681107679,          
                   7214.80159014479, 6743.7047361935, 6488.26377871286, 6211.21826512409, 
                   6034.49435836295, 5893.24179377874, 5751.40614476101, 5659.17644303175, 
                   5566.20784121872, 5501.27177798158, 5450.10258224782, 5333.80742396442, 
                   5310.64411661032, 5258.70862590589, 5250.09482100684, 5155.73346173091, 
                   5162.682699073};
    real lambda_cd[] = {0.0423641927686851, 0.04208184760082196, 0.04171911343741601, 
                        0.0412656667751845, 0.040786847157422354, 0.04016401532770846, 
                        0.03952678217090253, 0.038768168612482154, 0.037970025713875394, 
                        0.03709899678679481, 0.03611827981127893, 0.03508988386112143, 
                        0.033952093386970014, 0.032751432540774096, 0.031470352372237304, 
                        0.029918372881538424, 0.028470709464537725, 0.026827735084638545, 
                        0.025205059315509308, 0.02314750671281832, 0.021346124828306105};
    real lambda = 0.0433;

    int j;
    int total = sizeof(beta) / sizeof(beta[0]);

    real T = C_T(c, t);

    /* 获取beta和T，并计算lambda*/
    for(j=0; j<total; j++)
    {
        if(fabs(T - T_ref[j]) < 1e-1)
        {
            lambda = lambda_cd[j] + (16.0 * n * n * sigma * T_ref[j] * T_ref[j] * T_ref[j]) / (3.0 * beta[j]);
            Message0("beta = %g, delta_T = %g, lambda_cd = %g, lambda = %g\n", beta[j], T_Max_GLO - T_Min_GLO, lambda_cd[j], lambda);
            break;
        }
    }
    return lambda;  
}


/*输出保存数据*/
DEFINE_ON_DEMAND(save_file)
{
    FILE *fp;
    Thread *t;
    Domain *d;
    cell_t c;
    
    const char FILENAME[] = "temperature.txt";
    real position[ND_ND];

    if((fp = fopen(FILENAME, "w")) == NULL)
    {
        Message0("NO FILE\n", FILENAME);
        return;
    }
    else
    {
        fprintf(fp, "x y z temperature\n");
    }
    d = Get_Domain(1);
    thread_loop_c(t, d)
    {
        begin_c_loop(c, t)
        {
            real T = C_T(c, t);
            C_CENTROID(position, c, t);
            fprintf(fp, "%g %g %g %g\n", position[0], position[1], position[2], T);
        }
        end_c_loop(c, t)
    }
    fclose(fp);
    Message0("finished %s.\n", FILENAME);
}
