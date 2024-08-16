#include "udf.h"
#include <stdio.h>
#include <math.h>


float global_q1 = 0.00;
float global_q2 = 0.00;
float global_beta = 0.00;
float global_t1 = 0.00;
float global_t2 = 0.00;
float global_lambda = 0.0;



// DEFINE_ADJUST(adjust_gradient, d)
// {

// #if !RP_HOST
//     Thread *t;
//     cell_t c;

//     d = Get_Domain(1);
// #endif

// #if !RP_HOST   
//     thread_loop_c(t, d)
//     {
//         begin_c_loop(c, t)
//         {
//             C_UDSI(c, t, 0) = C_T_G(c, t)[0];
//             C_UDSI(c, t, 1) = C_T_G(c, t)[1];
//             C_UDSI(c, t, 2) = C_T_G(c, t)[2];

//         }
//         end_c_loop(c, t)
//     }
// #endif
// }

// /* 计算lambda */
// DEFINE_SOURCE(radiation, c, t, ds, eqn)
// {
//     /* 定义lambda中的参数 */
//     real n = 1.018501;
//     real sigma = 5.67 * pow(10, -8);
//     real Beta_int;
//     real lambda_rad;
//     real source;
    

    
//     real T_iter = C_T(c, t);
    
//     Beta_int = 1318.08396 + 28.59918 * T_iter - 0.02824 * pow(T_iter, 2) + (1.05058 * pow(10, -5)* pow(T_iter, 3));/*O-1*/
//     /*Beta_int = 33826.3057 - 155.98605 * T_iter + 0.25607 * pow(T_iter, 2) - (1.41853 * pow(10, -4)* pow(T_iter, 3));p-2*/
//     /* 获取beta和T，并计算lambda*/

//     C_UDMI(c, t, 0) = Beta_int;
//     C_UDMI(c, t, 1) = C_UDSI_G(c, t, 0)[0] + C_UDSI_G(c, t, 1)[1] + C_UDSI_G(c, t, 2)[2];

   
//     lambda_rad = (16.0 * pow(n, 2) * sigma * pow(T_iter, 3)) / (3.0 * Beta_int);
//     /*source = (16.0 * pow(n, 2) * sigma * pow(T_iter, 3)) / (3.0 * Beta_int) * C_T_G(c, t)[0];*/
//     source = lambda_rad * C_UDMI(c, t, 1);
//     ds[eqn] = (16.0 * pow(n, 2) * sigma * pow(T_iter, 3)) / (3.0 * Beta_int);

//     /*Message("Beta_int = %g, T_iter = %g, lambda_rad = %g\n", Beta_int, T_iter, lambda_rad);*/

//     return source;  
// }

DEFINE_PROPERTY(rho, c, t)
{
    real density;
    real T_iter = C_T(c, t);
    
    density = 134.37865 + 0.25437 * T_iter - 8.49351 * pow(10, -6) * pow(T_iter, 2);

    return density;
}

DEFINE_PROPERTY(lambda_eff, c, t)
{
    real lambda_eff;
    real n;
    real sigma = 5.67 * pow(10, -8);
    real Beta_int;
    real lambda_cd;
    real T_iter = C_T(c, t);

    /*Beta_int = Beta_int = 72284.60564 - 31.92112 * T_iter;
    lambda_cd = 0.04083 + 2.08441 * pow(10, -5) * T_iter - 4.2746 * pow(10, -8) * pow(T_iter, 2);*/

    Beta_int = global_beta - 31.97742 * T_iter;
    /*lambda_cd = 0.00749328 + 1.1847118 * pow(10, -5) * T_iter - 1.48368808 * pow(10, -8) * pow(T_iter, 2) + 0.93397118 * pow(10, -11)* pow(T_iter, 3);
    n = 17.10781 - 0.04529 * T_iter + 4.5792 * pow(10, -5) * pow(T_iter, 2) - 1.59131 * pow(10, -8) * pow(T_iter, 3);*/

    lambda_cd = 0.015 + global_lambda * pow(10, -6) * T_iter;
    n = -0.50062 + 0.00496 * T_iter - 5.13119 * pow(10, -6) * pow(T_iter, 2) + 1.61771 * pow(10, -9) * pow(T_iter, 3);


    lambda_eff = lambda_cd + (16 * sigma * pow(n, 2)) / (3 * Beta_int)  * pow(T_iter, 3);

    return lambda_eff;
}



DEFINE_PROFILE(heat_flux, t, i)
{
    real xc[ND_ND];
    real x;
    real y;
    face_t f;
    real R = 0.1;
    real r1;

  
    begin_f_loop(f, t)
    {
        F_CENTROID(xc, f, t);
        x = xc[0];
        y = xc[1];
        r1 = sqrt(pow(x - 7.10105, 2) + pow(y + 0.19728521, 2));
        if(r1 < R)
        {
            F_PROFILE(f, t, i) =  1300 * exp((-3 * ((pow(x - 7.10105, 2) + pow(y + 0.19728521, 2)) / pow(R, 2))));
        }
        else
        {
            F_PROFILE(f, t, i) = 300;
        }    
    }
    end_f_loop(f, t)
}


DEFINE_PROFILE(heat_flux_time_space, t, i)
{
    real xc[ND_ND];
    real x;
    real y;
    face_t f;
    real R = 0.1;
    real r;
    real Q_t;

    real time = CURRENT_TIME;


    if (time < 680)
    {
        begin_f_loop(f, t)
        {
            F_CENTROID(xc, f, t);
            x = xc[0];
            y = xc[1];
            
            Q_t = - ((global_q1 / 100) / 1600) * pow(x-400, 2) + (global_q1);
            r = sqrt(pow(x - 7.10105, 2) + pow(y + 0.19728521, 2));
            if(r < R)
            {
                F_PROFILE(f, t, i) =  Q_t * exp((-3 * ((pow(x - 7.10105, 2) + pow(y + 0.19728521, 2)) / pow(R, 2))));
            }
            else
            {
                F_PROFILE(f, t, i) = 300;
            }
        }
        end_f_loop(f, t)
    }
    else if (time < 2800)
    {
        begin_f_loop(f, t)
        {
            F_CENTROID(xc, f, t);
            x = xc[0];
            y = xc[1];
            
            Q_t = - ((global_q2 / 100) / 16900) * pow(x-1500, 2) + global_q2;
            r = sqrt(pow(x - 7.10105, 2) + pow(y + 0.19728521, 2));

            if(r < R)
            {
                F_PROFILE(f, t, i) =  Q_t * exp((-3 * ((pow(x - 7.10105, 2) + pow(y + 0.19728521, 2)) / pow(R, 2))));
            }
            else
            {
                F_PROFILE(f, t, i) = 300;
            }
        }
        end_f_loop(f, t)  
    }
    else
    {
        begin_f_loop(f, t)
        {
            F_CENTROID(xc, f, t);
            x = xc[0];
            y = xc[1];
            
            r = sqrt(pow(x - 7.10105, 2) + pow(y + 0.19728521, 2));

            if(r < R)
            {
                F_PROFILE(f, t, i) =  0;
            }
            else
            {
                F_PROFILE(f, t, i) = 300;
            }
        }
        end_f_loop(f, t)  
    }
        
}

DEFINE_PROFILE(heat_flux_time, t, i)
{

    face_t f;
    

    /* 交点*/
    real a = - global_q1 / pow(global_t1, 2);
    real b = - global_q2 / pow(2800 - global_t2, 2);
    real m_1 = (a * global_t1 - b * global_t2 + sqrt(pow(a * global_t1 - b * global_t2, 2) - (a - b) * (a * pow(global_t1, 2) - b * pow(global_t2, 2) + global_q1 - global_q2))) / (a - b);
    real m_2 = (a * global_t1 - b * global_t2 - sqrt(pow(a * global_t1 - b * global_t2, 2) - (a - b) * (a * pow(global_t1, 2) - b * pow(global_t2, 2) + global_q1 - global_q2))) / (a - b);

    real m;

    real time = CURRENT_TIME;
    if (m_1 > m_2)
    {
        m = m_1;
    }
    else
    {
        m = m_2;
    }

    if (time < m)
    {
        begin_f_loop(f, t)
        {
   
            F_PROFILE(f, t, i) =  a * pow(time - global_t1, 2) + global_q1;
          
        }
        end_f_loop(f, t)
    }
    else if (time < 2800)
    {
        begin_f_loop(f, t)
        {
            
            F_PROFILE(f, t, i) =  b * pow(time - global_t2, 2) + global_q2;
 
        }
        end_f_loop(f, t)  
    }
    else
    {
        begin_f_loop(f, t)
        {
       
            F_PROFILE(f, t, i) =  0;
 
        }
        end_f_loop(f, t)  
    }   
}


// /*输出保存数据*/
// DEFINE_ON_DEMAND(save_file)
// {
//     FILE *fp;
//     Thread *t;
//     Domain *d;
//     cell_t c;
    
//     const char FILENAME[] = "beta_temperature.txt";
//     real position[ND_ND];

//     if((fp = fopen(FILENAME, "w")) == NULL)
//     {
//         Message0("NO FILE\n", FILENAME);
//         return;
//     }
//     else
//     {
//         fprintf(fp, "x y z temperature beta\n");
//     }
//     d = Get_Domain(1);
//     thread_loop_c(t, d)
//     {
//         begin_c_loop(c, t)
//         {
//             real T = C_T(c, t);
//             real Beta_int = C_UDMI(c, t, 0);
//             /*C_UDMI(c, t, 1) = C_UDSI_G(c, t, 0)[0] + C_UDSI_G(c, t, 1)[1] + C_UDSI_G(c, t, 2)[2];*/

//             C_CENTROID(position, c, t);
//             fprintf(fp, "%g %g %g %g %g\n", position[0], position[1], position[2], T, Beta_int);
//         }
//         end_c_loop(c, t)
//     }
//     fclose(fp);
//     Message0("finished %s.\n", FILENAME);
// }


/* 读取文件数据 */
DEFINE_ON_DEMAND(read_file)
{
    FILE *fp;
   

    if((fp = fopen("./single_design.txt", "r")) == NULL)
    {
        Message0("file does not exit");
    }

    if(fscanf(fp, "%f %f %f %f %f %f", &global_q1, &global_q2, &global_t1, &global_t2, &global_lambda, &global_beta) != 6)
    {

        Message0("not extis");
        fclose(fp);
        return;
    }
    fclose(fp);
    
    Message0("设计变量：%f %f %f %f %f %f\n", global_q1, global_q2, global_t1, global_t2, global_lambda, global_beta);
}